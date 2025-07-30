import os
import re
import subprocess
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Tuple, Dict

from rich.console import Console
from tqdm import tqdm

console = Console(log_path=False, force_terminal=True, color_system="auto")


def check_dependencies():
    """Проверяет наличие radare2 и ripgrep в системе."""
    deps = {'r2': ['r2', '-h'], 'rg': ['rg', '--version']}
    for name, cmd in deps.items():
        try:
            subprocess.run(cmd, capture_output=True, check=True, text=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            console.print(
                f"[bold red]Критическая ошибка: Зависимость '{name}' не найдена. Установите ее и добавьте в PATH.[/bold red]")
            return False
    return True


class StrategyFind:
    def __init__(self, strategies, root_dir, debug, search_terms, ignore_case):
        self.root_dir = root_dir
        self.debug = debug
        self.search_terms = search_terms
        self.ignore_case = ignore_case
        self.r2_enabled = False
        self.rg_enabled = False
        for st in strategies:
            if st == 'r2':
                self.r2_enabled = True
                console.print(f"[bold green]Активарован поиск через radare2[/bold green] [bold red](r2)[/bold red]")
            if st == 'rg':
                self.rg_enabled = True
                console.print(f"[bold green]Активарован поиск через ripgrep[/bold green] [bold red](rg)[/bold red]")


    def process_file(self, filepath: Path) -> Tuple[Path, Dict[str, int], List[str]]:
        """
        Оркестратор анализа для одного файла с улучшенным логированием.
        """
        debug_log = [f"[bold cyan]Processing:[/] {filepath.relative_to(self.root_dir)}"]
        final_results = defaultdict(int)

        # --- Стратегия 1: Radare2 ---
        if self.r2_enabled:
            if self.debug: debug_log.append("[dim]Running Strategy 2: Radare2...[/dim]")
            r2_findings = self.search_with_radare2(filepath, debug_log)
            if r2_findings:
                debug_log.append(f"  [green]-> Radare2 Found:[/green] {dict(r2_findings)}")
                for term, count in r2_findings.items():
                    final_results[term] = max(final_results[term], count)

        # --- Стратегия 2: Ripgrep ---
        if self.rg_enabled:
            if self.debug: debug_log.append("[dim]Running Strategy 3: Ripgrep...[/dim]")
            rg_findings = self.search_with_ripgrep(filepath, debug_log)
            if rg_findings:
                debug_log.append(f"  [green]-> Ripgrep Found:[/green] {dict(rg_findings)}")
                for term, count in rg_findings.items():
                    final_results[term] = max(final_results[term], count)

        if final_results:
            debug_log.append(f"[bold magenta]Final Tally:[/bold magenta] {dict(final_results)}")

        return filepath, final_results, debug_log

    def search_with_radare2(self, filepath: Path, debug_log: list) -> dict[str, int]:
        """Стратегия 2: Глубокий анализ с помощью radare2."""
        results = defaultdict(int)
        command = ['r2', '-uuu', '-q', '-c', 'izz', str(filepath)]
        debug_log.append(f"R2 CMD: {' '.join(command)}")
        try:
            proc = subprocess.run(
                command, capture_output=True, encoding='utf-8', errors='ignore', timeout=60
            )
            if proc.returncode != 0 and proc.stderr:
                debug_log.append(f"[yellow]R2 returned error ({proc.returncode}): {proc.stderr.strip()}[/yellow]")
                return results

            r2_strings = proc.stdout.splitlines()
            debug_log.append(f"R2 extracted {len(r2_strings)} strings.")
            for term in self.search_terms:
                if self.ignore_case:
                    count = sum(1 for line in r2_strings if term.lower() in line.lower())
                else:
                    count = sum(1 for line in r2_strings if term in line)
                if count > 0: results[term] = count
        except subprocess.TimeoutExpired:
            debug_log.append(f"[bold yellow]R2 Timed Out[/bold yellow]")
        except Exception as e:
            debug_log.append(f"[bold red]R2 Critical Error: {e}[/bold red]")
        return results

    def search_with_ripgrep(self, filepath: Path, debug_log: list) -> dict[str, int]:
        """Стратегия 3: Поиск с помощью ripgrep."""
        results = defaultdict(int)
        for term in self.search_terms:
            command = ['rg', '--count-matches', '--text']
            if self.ignore_case:
                command.append('--ignore-case')
            else:
                command.append('--case-sensitive') # Явно указываем для надежности
            command.extend([term, str(filepath)])

            try:
                proc = subprocess.run(
                    command, capture_output=True, text=True, timeout=60
                )
                # rg выводит "N\n", если есть совпадения, и ничего, если нет.
                if proc.stdout.strip():
                    try:
                        count = int(proc.stdout.strip())
                        if count > 0:
                            results[term] = count
                    except ValueError:
                        debug_log.append(
                            f"[orange3]RG returned non-integer for term '{term}': {proc.stdout.strip()}[/orange3]")
            except subprocess.TimeoutExpired:
                debug_log.append(f"[bold yellow]RG Timed Out for term '{term}'[/bold yellow]")
            except Exception as e:
                debug_log.append(f"[bold red]RG Critical Error for term '{term}': {e}[/bold red]")
        return results


class FindFiles:
    def __init__(self, root_dir: str, search_terms: list, strategies: list, thread: int, debug: bool, ignore_case: bool):
        """
        Поиск данных в файлах
        :param root_dir: Стартовая папка для поиска
        :param search_terms: Искомые слова
        :param strategies: r2 и/или rg
        :param thread: Колличество потоков
        :param debug: Включить debug режим
        :return:
        """

        self.root_dir = Path(root_dir).resolve()
        self.search_terms = search_terms
        self.thread = thread
        self.debug = debug
        self.strategies = StrategyFind(strategies, self.root_dir, self.debug, self.search_terms, ignore_case)


    def get_all_filepaths(self):
        all_files = [f for f in self.root_dir.rglob('*') if f.is_file() and f.stat().st_size > 0]
        if not all_files:
            console.print("[yellow]No non-empty files found for analysis.[/yellow]")
            sys.exit(0)
        return all_files

    def start_find(self):
        threads = int(os.cpu_count() / 2)
        if not check_dependencies(): return
        if not self.root_dir.is_dir():
            console.print(f"[bold red]Ошибка: Директория '{self.root_dir}' не найдена.[/bold red]")
            return

        console.print(f"[bold green]Директория для поиска:[/bold green] [cyan]{self.root_dir}[/cyan]")
        console.print(
            f"[bold green]DEBUG Режим:[/bold green] {'[bold green]ON[/]' if self.debug else '[bold red]OFF[/]'}")
        console.print(f"[bold green]Колличество потоков:[/bold green] [cyan]{threads}[/cyan]")
        console.print(f"[bold green]Ищем {len(self.search_terms)} входжений...[/bold green]")
        all_filepaths = self.get_all_filepaths()
        console.print(f"[bold green]Колличество файлов:[/bold green] [cyan]{len(all_filepaths)}[/cyan]")

        aggregated_results = defaultdict(lambda: defaultdict(int))

        executor = None
        progress_bar = None
        try:
            executor = ThreadPoolExecutor(max_workers=threads)
            future_to_file = {executor.submit(self.strategies.process_file, filepath): filepath for filepath in all_filepaths}
            progress_bar = tqdm(as_completed(future_to_file), total=len(all_filepaths), desc="Analyzing files", unit="file")

            for future in progress_bar:
                try:
                    filepath, findings, debug_log = future.result()
                    if self.debug and (findings or len(debug_log) > 1):
                        console.rule(f"[dim]{filepath.name}[/dim]", align="left")
                        for line in debug_log: console.print(line)

                    if findings:
                        for term, count in findings.items():
                            aggregated_results[term][str(filepath)] = count
                except Exception as e:
                    filepath = future_to_file[future]
                    console.print(f"[bold red]Error processing result for {filepath}: {e}[/bold red]")


        except KeyboardInterrupt:
            console.print("\n[bold yellow]Процесс прерван пользователем. Завершение...[/bold yellow]")
            if progress_bar:
                progress_bar.close()
            if executor:
                executor.shutdown(wait=False, cancel_futures=True)
            sys.exit(1)
        finally:
            if executor:
                executor.shutdown(wait=True)  # Обычное завершение, если не было прерывания

        # Вывод
        console.print("\n\n[bold underline magenta]===== SEARCH RESULTS =====[/bold underline magenta]\n")
        if not aggregated_results:
            console.print("[yellow]No matches found.[/yellow]")
            return

        for term in sorted(aggregated_results.keys()):
            files_found = aggregated_results[term]
            console.print(f"Term [bold yellow]'{term}'[/bold yellow] was found in:")
            for filepath_str, count in sorted(files_found.items()):
                console.print(f"  - [cyan]{filepath_str}[/cyan] [[bold green]{count}[/bold green] count]")
            console.print("")

if __name__ == "__main__":
    ff = FindFiles(
        '.',
        ['SM-G950FZ', 'G950FZKA', 'SER'], ['rg'], 32, True, False)
    ff.start_find()
