import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { ApiService } from '../../services/api.service';
import { NotificationService } from '../../services/notification.service';
import { DataRefreshService } from '../../services/data-refresh.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-dashboard-paciente',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './dashboard-paciente.component.html',
  styleUrl: './dashboard-paciente.component.css'
})
export class DashboardPacienteComponent implements OnInit, OnDestroy {
  user: any;
  activeTab = 'citas';
  citas: any[] = [];
  medicos: any[] = [];
  medicosFiltrados: any[] = [];
  especialidades: any[] = [];
  historial: any[] = [];
  loading = false;
  private refreshSub: Subscription | null = null;

  showConfirmCancel = false;
  citaAEliminar: any = null;

  nuevaCita: any = { medico_id: '', fecha: '', hora: '', tipo_consulta: '' };
  minDate = new Date().toISOString().split('T')[0];

  showReprogramar = false;
  citaReprogramar: any = null;
  nuevaFecha = '';
  nuevaHora = '';
  motivoReprogramacion = '';
  loadingReprogramar = false;

  constructor(
    private authService: AuthService,
    private api: ApiService,
    private router: Router,
    private notification: NotificationService,
    private refreshService: DataRefreshService
  ) {}

  ngOnInit(): void {
    this.user = this.authService.getUser();
    if (!this.user || this.authService.getUserRole() !== 'AFILIADO') {
      this.router.navigate(['/login']);
      return;
    }
    this.loadCitas();
    this.loadMedicos();
    this.loadEspecialidades();
    this.loadHistorial();

    this.refreshSub = this.refreshService.refresh$.subscribe((type: string) => {
      if (type === 'citas' || type === 'all') this.loadCitas();
      if (type === 'historial' || type === 'all') this.loadHistorial();
    });
  }

  ngOnDestroy(): void {
    this.refreshSub?.unsubscribe();
  }

  loadHistorial(): void {
    if (this.user.paciente_id) {
      this.api.getHistorialPaciente(this.user.paciente_id).subscribe({
        next: (data: any) => this.historial = data,
        error: (err: any) => console.error(err)
      });
    }
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
      this.notification.warning(`No hay médicos disponibles para ${especialidad}`);
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

    this.api.createCita(this.nuevaCita).subscribe({
      next: () => {
        this.notification.success('Cita agendada exitosamente');
        this.loading = false;
        this.nuevaCita = { medico_id: '', fecha: '', hora: '', tipo_consulta: '' };
        this.medicosFiltrados = [];
        this.loadCitas();
        this.refreshService.triggerRefresh('citas');
        this.activeTab = 'citas';
      },
      error: (err: any) => {
        this.loading = false;
        this.notification.error(err.error?.error || 'Error al agendar cita');
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
        this.notification.success('Cita cancelada correctamente');
        this.loadCitas();
        this.refreshService.triggerRefresh('citas');
      },
      error: (err: any) => this.notification.error(err.error?.error || 'Error al cancelar')
    });

    this.showConfirmCancel = false;
    this.citaAEliminar = null;
  }

  cerrarModal(): void {
    this.showConfirmCancel = false;
    this.citaAEliminar = null;
  }

  abrirReprogramar(cita: any): void {
    this.citaReprogramar = cita;
    this.nuevaFecha = '';
    this.nuevaHora = '';
    this.motivoReprogramacion = '';
    this.showReprogramar = true;
  }

  cerrarReprogramar(): void {
    this.showReprogramar = false;
    this.citaReprogramar = null;
  }

  Reprogramar(): void {
    if (!this.nuevaFecha || !this.nuevaHora) {
      this.notification.error('Seleccione nueva fecha y hora');
      return;
    }

    this.loadingReprogramar = true;
    this.api.createReprogramacion({
      cita_id: this.citaReprogramar.id,
      nueva_fecha: this.nuevaFecha,
      nueva_hora: this.nuevaHora,
      motivo: this.motivoReprogramacion
    }).subscribe({
      next: () => {
        this.notification.success('Solicitud de reprogramación enviada');
        this.loadingReprogramar = false;
        this.cerrarReprogramar();
        this.loadCitas();
        this.refreshService.triggerRefresh('citas');
      },
      error: (err: any) => {
        this.notification.error(err.error?.error || 'Error al reprogramar');
        this.loadingReprogramar = false;
      }
    });
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}