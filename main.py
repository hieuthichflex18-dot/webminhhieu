from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm

from config import CONFIG
from downloader import TikTokDownloader
from uploader import TikTokUploader
from pipeline import ReupPipeline
from tts_engine import TTSEngine, VOICES

console = Console()


def banner():
    console.print(Panel.fit(
        "[bold cyan]🎬 TOOL REUP VIDEO AI[/bold cyan]\n"
        "[green]Link → Text → Rewrite → Voice → Video → Upload[/green]",
        border_style="cyan",
    ))


def menu():
    console.print("\n[bold]📋 MENU:[/bold]")
    console.print("  [cyan]1[/cyan]. 🚀 REUP TỰ ĐỘNG")
    console.print("  [cyan]2[/cyan]. 📥 Tải video")
    console.print("  [cyan]3[/cyan]. 🎙️ Tạo giọng nói từ text")
    console.print("  [cyan]4[/cyan]. 🎬 Tạo video từ prompt")
    console.print("  [cyan]5[/cyan]. 📤 Đăng TikTok")
    console.print("  [cyan]6[/cyan]. ✅ Check login TikTok")
    console.print("  [cyan]7[/cyan]. 📋 Danh sách giọng nói")
    console.print("  [cyan]0[/cyan]. Thoát")


def pick_voice():
    voices_list = list(VOICES.keys())
    for i, key in enumerate(voices_list, 1):
        console.print(f"  {i}. {key}")
    c = Prompt.ask("Chọn giọng", default="adam_vi")
    try:
        return voices_list[int(c) - 1]
    except Exception:
        return c if c in VOICES else "adam_vi"


def cmd_pipeline():
    url = Prompt.ask("[bold blue]🔗 Link video[/bold blue]")
    console.print("\n[bold]🎙️ Chọn giọng:[/bold]")
    voice = pick_voice()
    auto = Confirm.ask("📤 Tự động đăng TikTok?", default=False)
    pipeline = ReupPipeline(CONFIG)
    result = pipeline.run(url, voice_key=voice, auto_upload=auto)
    if result["success"]:
        console.print(Panel.fit(
            f"[bold green]✅ HOÀN TẤT![/bold green]\n\n"
            f"📹 Video: {result.get('video_path')}\n"
            f"📝 Tiêu đề: {result.get('title')}",
            border_style="green",
        ))


def cmd_tts():
    text = Prompt.ask("[bold blue]Văn bản[/bold blue]")
    console.print("\n[bold]🎙️ Giọng:[/bold]")
    voice = pick_voice()
    tts = TTSEngine(CONFIG["paths"]["audio"])
    out = tts.text_to_speech(text, voice_key=voice)
    console.print(f"[green]✅ {out}[/green]")


def cmd_create_video():
    prompt = Prompt.ask("[bold blue]Nội dung[/bold blue]")
    use_ai = Confirm.ask("🤖 AI viết lại?", default=True)
    if use_ai:
        from rewriter import ContentRewriter
        rw = ContentRewriter(CONFIG["api"]["base_url"],
                             CONFIG["api"]["api_key"],
                             CONFIG["api"]["default_model"])
        console.print("[yellow]⏳ AI viết lại...[/yellow]")
        prompt = rw.rewrite(prompt)

    console.print("\n[bold]🎙️ Giọng:[/bold]")
    voice = pick_voice()
    tts = TTSEngine(CONFIG["paths"]["audio"])
    audio = str(Path(CONFIG["paths"]["audio"]) / "voice_custom.mp3")
    tts.text_to_speech(prompt, voice_key=voice, output_path=audio)

    from video_maker import VideoMaker
    maker = VideoMaker(CONFIG)
    video = maker.create_video(prompt, audio)
    console.print(f"[green]✅ Video: {video}[/green]")


def cmd_list_voices():
    table = Table(title="🎙️ Danh sách giọng", border_style="cyan")
    table.add_column("Key", style="cyan")
    table.add_column("Voice", style="green")
    for k, v in VOICES.items():
        table.add_row(k, v)
    console.print(table)


def main():
    banner()
    while True:
        menu()
        c = Prompt.ask("Chọn", choices=[str(i) for i in range(8)], default="1")
        if c == "0":
            break
        elif c == "1":
            cmd_pipeline()
        elif c == "2":
            url = Prompt.ask("🔗 URL")
            TikTokDownloader(CONFIG["paths"]["downloads"]).download(url)
        elif c == "3":
            cmd_tts()
        elif c == "4":
            cmd_create_video()
        elif c == "5":
            console.print("[dim]Dùng CLI riêng[/dim]")
        elif c == "6":
            u = TikTokUploader(CONFIG["tiktok_cookies"])
            console.print("[green]✅ OK[/green]" if u.check_login()
                          else "[red]❌ Cookie lỗi[/red]")
        elif c == "7":
            cmd_list_voices()


if __name__ == "__main__":
    main()
