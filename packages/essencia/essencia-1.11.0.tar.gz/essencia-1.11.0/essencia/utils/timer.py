"""
Timer utilities for tracking durations.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, Callable

import flet as ft


class VisitTimer(ft.Container):
    """
    Timer for tracking visit duration.
    Shows elapsed time and allows finishing the visit.
    """
    
    def __init__(
        self,
        visit_id: str,
        on_finish: Optional[Callable] = None,
        start_time: Optional[datetime] = None
    ):
        super().__init__()
        self.visit_id = visit_id
        self.on_finish = on_finish
        self.start_time = start_time or datetime.now()
        self.is_running = True
        
        # UI elements
        self.timer_text = ft.Text(
            "00:00:00",
            size=24,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.PRIMARY
        )
        self.status_text = ft.Text(
            "Consulta em andamento",
            size=14,
            color=ft.Colors.SECONDARY
        )
        self.finish_button = ft.ElevatedButton(
            "Finalizar Consulta",
            icon=ft.Icons.STOP,
            on_click=self._handle_finish,
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.ERROR
        )
        self.pause_button = ft.IconButton(
            icon=ft.Icons.PAUSE,
            tooltip="Pausar",
            on_click=self._toggle_pause
        )
        
        # Set up container content
        self.content = ft.Card(
            content=ft.Container(
                padding=20,
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(
                                    ft.Icons.TIMER,
                                    size=30,
                                    color=ft.Colors.PRIMARY
                                ),
                                ft.Text(
                                    "Cronômetro da Consulta",
                                    size=18,
                                    weight=ft.FontWeight.BOLD
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                        ft.Divider(),
                        self.timer_text,
                        self.status_text,
                        ft.Row(
                            controls=[
                                self.pause_button,
                                self.finish_button
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=10
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10
                )
            )
        )
        self.width = 300
    
    def did_mount(self):
        """Start timer when component mounts"""
        self.page.run_task(self._update_timer)
    
    async def _update_timer(self):
        """Update timer display every second"""
        while self.page and self.is_running:
            if hasattr(self, '_paused') and self._paused:
                await asyncio.sleep(1)
                continue
                
            elapsed = datetime.now() - self.start_time
            
            # Format elapsed time
            hours = int(elapsed.total_seconds() // 3600)
            minutes = int((elapsed.total_seconds() % 3600) // 60)
            seconds = int(elapsed.total_seconds() % 60)
            
            self.timer_text.value = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
            # Update status based on duration
            if elapsed.total_seconds() > 3600:  # More than 1 hour
                self.timer_text.color = ft.Colors.ERROR
                self.status_text.value = "Consulta longa - considere finalizar"
                self.status_text.color = ft.Colors.ERROR
            elif elapsed.total_seconds() > 2400:  # More than 40 minutes
                self.timer_text.color = ft.Colors.WARNING
                self.status_text.value = "Tempo normal excedido"
                self.status_text.color = ft.Colors.WARNING
            
            self.update()
            await asyncio.sleep(1)
    
    def _toggle_pause(self, e):
        """Toggle pause state"""
        if hasattr(self, '_paused') and self._paused:
            self._paused = False
            self.pause_button.icon = ft.Icons.PAUSE
            self.pause_button.tooltip = "Pausar"
            self.status_text.value = "Consulta em andamento"
            self.status_text.color = ft.Colors.SECONDARY
        else:
            self._paused = True
            self.pause_button.icon = ft.Icons.PLAY_ARROW
            self.pause_button.tooltip = "Continuar"
            self.status_text.value = "Consulta pausada"
            self.status_text.color = ft.Colors.WARNING
        self.update()
    
    async def _handle_finish(self, e):
        """Handle finish button click"""
        # Calculate final duration
        elapsed = datetime.now() - self.start_time
        duration_minutes = int(elapsed.total_seconds() / 60)
        
        # Show confirmation dialog
        async def confirm_finish(e):
            self.is_running = False
            self.page.close(dialog)
            
            if self.on_finish:
                await self.on_finish(self.visit_id, duration_minutes)
        
        async def cancel_finish(e):
            self.page.close(dialog)
        
        dialog = ft.AlertDialog(
            title=ft.Text("Finalizar Consulta?"),
            content=ft.Text(
                f"Duração total: {duration_minutes} minutos\n"
                f"Deseja finalizar esta consulta?"
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=cancel_finish),
                ft.ElevatedButton(
                    "Finalizar",
                    on_click=confirm_finish,
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.ERROR
                )
            ]
        )
        
        self.page.open(dialog)
    
    def stop(self):
        """Stop the timer"""
        self.is_running = False


class CountdownTimer(ft.Container):
    """
    Countdown timer for appointments or tasks.
    """
    
    def __init__(
        self,
        duration_seconds: int,
        on_complete: Optional[Callable] = None,
        warning_seconds: int = 300  # 5 minutes
    ):
        super().__init__()
        self.duration = duration_seconds
        self.remaining = duration_seconds
        self.on_complete = on_complete
        self.warning_seconds = warning_seconds
        self.is_running = True
        
        # UI elements
        self.timer_text = ft.Text(
            self._format_time(duration_seconds),
            size=32,
            weight=ft.FontWeight.BOLD
        )
        self.progress_bar = ft.ProgressBar(
            width=250,
            height=10,
            value=1.0,
            color=ft.Colors.PRIMARY
        )
        self.status_text = ft.Text(
            "Tempo restante",
            size=14,
            color=ft.Colors.SECONDARY
        )
        
        # Set up container content
        self.content = ft.Column(
            controls=[
                self.timer_text,
                self.progress_bar,
                self.status_text
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        )
        self.padding = 20
    
    def did_mount(self):
        """Start countdown when mounted"""
        self.page.run_task(self._countdown)
    
    async def _countdown(self):
        """Countdown logic"""
        while self.page and self.is_running and self.remaining > 0:
            await asyncio.sleep(1)
            self.remaining -= 1
            
            # Update display
            self.timer_text.value = self._format_time(self.remaining)
            self.progress_bar.value = self.remaining / self.duration
            
            # Update colors based on remaining time
            if self.remaining <= 60:  # Last minute
                self.timer_text.color = ft.Colors.ERROR
                self.progress_bar.color = ft.Colors.ERROR
                self.status_text.value = "Tempo esgotando!"
                self.status_text.color = ft.Colors.ERROR
            elif self.remaining <= self.warning_seconds:
                self.timer_text.color = ft.Colors.WARNING
                self.progress_bar.color = ft.Colors.WARNING
                self.status_text.value = f"Atenção: {self.remaining // 60} minutos restantes"
                self.status_text.color = ft.Colors.WARNING
            
            self.update()
        
        # Timer completed
        if self.remaining <= 0 and self.on_complete:
            await self.on_complete()
    
    def _format_time(self, seconds: int) -> str:
        """Format seconds as HH:MM:SS or MM:SS"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    def pause(self):
        """Pause the countdown"""
        self.is_running = False
    
    def resume(self):
        """Resume the countdown"""
        self.is_running = True
        self.page.run_task(self._countdown)
    
    def stop(self):
        """Stop the countdown"""
        self.is_running = False
        self.remaining = 0