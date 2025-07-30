import datetime
import json
import os
import time
from typing import cast, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader
from openai import OpenAI
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

from ai18n.config import conf
from ai18n.message import Message

MODEL_TOKEN_LIMITS: Dict[str, int] = {
    "gpt-4": 8192,
    "gpt-4-0613": 8192,
    "gpt-4-1106-preview": 128000,
    "gpt-4-0125-preview": 128000,
    "gpt-3.5-turbo": 4096,
    "gpt-3.5-turbo-16k": 16384,
}

console = Console()


class OpenAIMessageTranslator:
    def __init__(
        self,
        api_key: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> None:
        self.model: str = model or "gpt-4"
        self.temperature: float = temperature or 0.3
        self.client = OpenAI(api_key=api_key)

        template_dir: str = conf.get("template_folder") or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "templates"
        )

        console.print(f"[bold green]Using template folder:[/bold green] {template_dir}")
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def estimate_token_usage(
        self, msgid: str, langs: List[str], existing_translations: Dict[str, str]
    ) -> int:
        base_prompt_tokens = 200
        msgid_tokens = len(msgid) // 4
        ref_tokens = sum(len(existing_translations.get(lang, "")) // 4 for lang in langs)
        return base_prompt_tokens + msgid_tokens * len(langs) + ref_tokens

    def build_prompt(self, message: Message, langs: List[str]) -> str:
        template = self.env.get_template("prompt.jinja")

        context = {
            "languages": langs,
            "msgid": message.msgid,
            "occurances": message.occurances or [],
            "extra_context": conf.get("prompt_extra_context"),
            "other_languages": {
                lang: message.po_translations.get(lang, "")
                for lang in langs
                if message.po_translations.get(lang)
            },
        }

        return template.render(context) or ""

    def execute_prompt(
        self,
        message: Message,
        langs: List[str],
        dry_run: bool = False,
        verbose: bool = False,
    ) -> Dict[str, str]:
        prompt = self.build_prompt(message, langs)

        if verbose:
            console.rule(f"[blue]Prompt for: {message.msgid[:60]}")
            console.print(prompt)

        if dry_run:
            return {}

        max_total_tokens = MODEL_TOKEN_LIMITS.get(self.model, 4096)
        reserved_input_tokens = 2000 if max_total_tokens > 8000 else 1000
        max_response_tokens = max_total_tokens - reserved_input_tokens

        try:
            start = time.time()
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional translator proficient in multiple languages.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_response_tokens,
                temperature=self.temperature,
            )
            response_text = response.choices[0].message.content.strip()
            duration = time.time() - start

            if verbose:
                console.print(f"[green]✓ Response in {duration:.1f}s[/green]")
                console.print(response_text)

            return cast(Dict[str, str], json.loads(response_text))
        except json.JSONDecodeError:
            console.print("[red]✖ JSON parsing error from OpenAI response[/red]")
        except Exception as e:
            console.print(f"[red]✖ OpenAI API error:[/red] {e}")
        return cast(Dict[str, str], {})

    def translate_message(
        self,
        message: Message,
        force: bool = False,
        dry_run: bool = False,
        verbose: bool = False,
    ) -> None:
        if not (message.requires_translation() or force):
            return

        target_langs: List[str] = conf["target_languages"]
        existing_translations = message.po_translations
        max_token_budget = MODEL_TOKEN_LIMITS.get(self.model, 4096) - 2000

        batches: List[List[str]] = []
        batch: List[str] = []
        budget = 0

        for lang in target_langs:
            tokens = self.estimate_token_usage(
                message.msgid, [lang], existing_translations
            )
            if budget + tokens > max_token_budget and batch:
                batches.append(batch)
                batch = [lang]
                budget = tokens
            else:
                batch.append(lang)
                budget += tokens
        if batch:
            batches.append(batch)

        full_result: Dict[str, str] = {}
        for batch_langs in batches:
            console.print(f"[dim]Translating to:[/dim] {', '.join(batch_langs)}")
            result = self.execute_prompt(
                message, langs=batch_langs, dry_run=dry_run, verbose=verbose
            )
            full_result.update(result)

        if full_result and not dry_run:
            message.merge_ai_output(full_result)
            message.update_metadata(self.model, datetime.datetime.now())

    def translate(
        self,
        messages: List[Message],
        force: bool = False,
        dry_run: bool = False,
        verbose: bool = False,
    ) -> None:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            transient=True,
        ) as progress:
            task = progress.add_task(
                "[bold blue]Translating messages...", total=len(messages)
            )

            for message in messages:
                progress.update(
                    task,
                    description=f"[blue]Translating:[/blue] {message.msgid[:50]}...",
                )
                self.translate_message(
                    message, force=force, dry_run=dry_run, verbose=verbose
                )
                progress.advance(task)
