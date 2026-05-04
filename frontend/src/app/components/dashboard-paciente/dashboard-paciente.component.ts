import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-dashboard-paciente',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './dashboard-paciente.component.html',
  styleUrl: './dashboard-paciente.component.css'
})
export class DashboardPacienteComponent implements OnInit {
  user: any;
  activeTab = 'citas';
  citas: any[] = [];
  medicos: any[] = [];
  historial: any[] = [];
  loading = false;
  message = '';
  messageType = '';
  showNotification = false;
  notificationType = '';
  notificationMessage = '';
  
  nuevaCita: any = { medico_id: '', fecha: '', hora: '', tipo_consulta: 'Medicina General' };
  minDate = new Date().toISOString().split('T')[0];

  showNotify(message: string, type: string, duration = 3000): void {
    this.notificationMessage = message;
    this.notificationType = type;
    this.showNotification = true;
    setTimeout(() => this.showNotification = false, duration);
  }

  constructor(private authService: AuthService, private api: ApiService, private router: Router) {}

  ngOnInit(): void {
    this.user = this.authService.getUser();
    if (!this.user || this.authService.getUserRole() !== 'paciente') {
      this.router.navigate(['/login']);
      return;
    }
    this.loadCitas();
    this.loadMedicos();
  }

  loadCitas(): void {
    this.api.getCitas().subscribe({
      next: (data: any) => this.citas = data,
      error: (err: any) => console.error(err)
    });
  }

  loadMedicos(): void {
    this.api.getMedicos().subscribe({
      next: (data: any) => this.medicos = data,
      error: (err: any) => console.error(err)
    });
  }

  agendarCita(): void {
    this.loading = true;
    this.message = '';
    
    this.api.createCita(this.nuevaCita).subscribe({
      next: () => {
        this.message = 'Cita agendada exitosamente';
        this.messageType = 'success';
        this.loading = false;
        this.showNotify(this.message, 'success');
        this.nuevaCita = { medico_id: '', fecha: '', hora: '', tipo_consulta: 'Medicina General' };
        this.loadCitas();
        this.activeTab = 'citas';
      },
      error: (err: any) => {
        this.message = err.error?.error || 'Error al agendar cita';
        this.messageType = 'error';
        this.loading = false;
        this.showNotify(this.message, 'error');
      }
    });
  }

  cancelarCita(id: number): void {
    if (confirm('¿Está seguro de cancelar esta cita?')) {
      this.api.deleteCita(id).subscribe({
        next: () => {
          this.loadCitas();
          this.showNotify('Cita cancelada', 'success');
        },
        error: (err: any) => this.showNotify(err.error?.error || 'Error al cancelar', 'error')
      });
    }
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}