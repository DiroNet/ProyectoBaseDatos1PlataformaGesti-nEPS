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
  medicosFiltrados: any[] = [];
  especialidades: any[] = [];
  historial: any[] = [];
  loading = false;
  message = '';
  messageType = '';
  showNotification = false;
  notificationType = '';
  notificationMessage = '';
  
  // Modal de confirmación
  showConfirmCancel = false;
  citaAEliminar: any = null;
  
  nuevaCita: any = { medico_id: '', fecha: '', hora: '', tipo_consulta: '' };
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
    this.loadEspecialidades();
  }

  loadCitas(): void {
    this.api.getCitas().subscribe({
      next: (data: any) => this.citas = data,
      error: (err: any) => console.error(err)
    });
  }

  loadMedicos(): void {
    this.api.getMedicos().subscribe({
      next: (data: any) => {
        this.medicos = data;
        this.medicosFiltrados = [];
      },
      error: (err: any) => console.error(err)
    });
  }

  loadEspecialidades(): void {
    this.api.getEspecialidades().subscribe({
      next: (data: any) => this.especialidades = data,
      error: (err: any) => console.error(err)
    });
  }

  onEspecialidadChange(): void {
    const especialidad = this.nuevaCita.tipo_consulta;
    this.nuevaCita.medico_id = '';
    
    if (!especialidad) {
      this.medicosFiltrados = [];
      return;
    }
    
    this.medicosFiltrados = this.medicos.filter(m => 
      m.especialidad && m.especialidad.toLowerCase() === especialidad.toLowerCase()
    );
    
    if (this.medicosFiltrados.length === 0) {
      this.showNotify(`No hay médicos disponibles para ${especialidad}`, 'error');
    }
  }

  onMedicoChange(): void {
    const medico = this.medicosFiltrados.find(m => m.id === Number(this.nuevaCita.medico_id));
    if (medico && medico.especialidad) {
      this.nuevaCita.tipo_consulta = medico.especialidad;
    }
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
        this.nuevaCita = { medico_id: '', fecha: '', hora: '', tipo_consulta: '' };
        this.medicosFiltrados = [];
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

  cancelarCita(cita: any): void {
    this.citaAEliminar = cita;
    this.showConfirmCancel = true;
  }

  confirmarCancelar(): void {
    if (!this.citaAEliminar) return;
    
    this.api.deleteCita(this.citaAEliminar.id).subscribe({
      next: () => {
        this.showNotify('Cita cancelada correctamente', 'success');
        this.loadCitas();
      },
      error: (err: any) => this.showNotify(err.error?.error || 'Error al cancelar', 'error')
    });
    
    this.showConfirmCancel = false;
    this.citaAEliminar = null;
  }

  cerrarModal(): void {
    this.showConfirmCancel = false;
    this.citaAEliminar = null;
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}