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
  selector: 'app-dashboard-medico',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './dashboard-medico.component.html',
  styleUrls: ['./dashboard-medico.component.css']
})
export class DashboardMedicoComponent implements OnInit, OnDestroy {
  user: any;
  medicoId = 0;
  activeTab = 'agenda';
  filterFecha = '';
  filterEstado = '';
  filterView = 'all';
  citas: any[] = [];
  disponibilidad: any[] = [];
  pacientes: any[] = [];
  loading = false;

  nuevaDisp: any = { dia_semana: '1', hora_inicio: '08:00', hora_fin: '17:00' };
  nuevoHistorial: any = { paciente_id: '', diagnostico: '', tratamiento: '', observaciones: '', cita_id: null };
  citasPaciente: any[] = [];
  citaSeleccionada: any = null;

  reprogramaciones: any[] = [];

  get reprogramacionesPendientes(): number {
    return this.reprogramaciones.filter(r => r.estado === 'pendiente').length;
  }

  private refreshSub: Subscription | null = null;

  constructor(
    private authService: AuthService,
    private api: ApiService,
    private router: Router,
    private notification: NotificationService,
    private refreshService: DataRefreshService
  ) {}

  ngOnDestroy(): void {
    this.refreshSub?.unsubscribe();
  }

  ngOnInit(): void {
    this.user = this.authService.getUser();
    if (!this.user || this.authService.getUserRole() !== 'PROFESIONAL') {
      this.router.navigate(['/login']);
      return;
    }
    this.medicoId = this.user.medico_id || 0;
    if (!this.medicoId) {
      this.notification.error('Error: No se encontró el ID del médico');
      return;
    }
    this.loadCitas();
    this.loadDisponibilidad();
    this.loadPacientes();

    this.refreshSub = this.refreshService.refresh$.subscribe((type: string) => {
      if (type === 'citas' || type === 'all') this.loadCitas();
      if (type === 'disponibilidad' || type === 'all') this.loadDisponibilidad();
      if (type === 'pacientes' || type === 'all') this.loadPacientes();
      if (type === 'reprogramaciones' || type === 'all') this.loadReprogramaciones();
    });

    this.loadReprogramaciones();
  }

  getLocalDateString(): string {
    const formatter = new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Bogota' });
    return formatter.format(new Date());
  }

  loadCitas(): void {
    const filters: any = { medico_id: this.medicoId };

    if (this.filterView === 'today') {
      const today = this.getLocalDateString();
      filters.fecha = today;
      this.filterFecha = today;
    } else if (this.filterFecha) {
      filters.fecha = this.filterFecha;
    }

    if (this.filterEstado) filters.estado = this.filterEstado;

    this.api.getCitas(filters).subscribe({
      next: (data: any) => this.citas = data,
      error: (err: any) => console.error(err)
    });
  }

  onFilterViewChange(): void {
    if (this.filterView === 'all') {
      this.filterFecha = '';
    }
    this.loadCitas();
  }

  loadDisponibilidad(): void {
    this.api.getDisponibilidadMedico(this.medicoId).subscribe({
      next: (data: any) => this.disponibilidad = data,
      error: (err: any) => console.error(err)
    });
  }

  loadPacientes(): void {
    this.api.getPacientes().subscribe({
      next: (data: any) => this.pacientes = data,
      error: (err: any) => console.error(err)
    });
  }

  loadReprogramaciones(): void {
    this.api.getReprogramaciones().subscribe({
      next: (data: any) => this.reprogramaciones = data,
      error: (err: any) => console.error(err)
    });
  }

  aprobarReprogramacion(id: number): void {
    this.api.updateReprogramacion(id, { estado: 'aprobada' }).subscribe({
      next: () => {
        this.notification.success('Reprogramación aprobada');
        this.loadReprogramaciones();
        this.loadCitas();
        this.refreshService.triggerRefresh('citas');
        this.refreshService.triggerRefresh('reprogramaciones');
      },
      error: (err: any) => this.notification.error(err.error?.error || 'Error al aprobar')
    });
  }

  rechazarReprogramacion(id: number): void {
    this.api.updateReprogramacion(id, { estado: 'rechazada' }).subscribe({
      next: () => {
        this.notification.success('Reprogramación rechazada');
        this.loadReprogramaciones();
        this.refreshService.triggerRefresh('reprogramaciones');
      },
      error: (err: any) => this.notification.error(err.error?.error || 'Error al rechazar')
    });
  }

  confirmarCita(id: number): void {
    this.api.updateCita(id, { estado: 'confirmada' }).subscribe({
      next: () => {
        this.notification.success('Cita confirmada');
        this.loadCitas();
        this.refreshService.triggerRefresh('citas');
      },
      error: (err: any) => this.notification.error(err.error?.error || 'Error al confirmar')
    });
  }

  rechazarCita(id: number): void {
    this.api.updateCita(id, { estado: 'cancelada' }).subscribe({
      next: () => {
        this.notification.success('Cita cancelada');
        this.loadCitas();
        this.refreshService.triggerRefresh('citas');
      },
      error: (err: any) => this.notification.error(err.error?.error || 'Error al cancelar')
    });
  }

  completarCita(id: number): void {
    this.api.updateCita(id, { estado: 'completada' }).subscribe({
      next: () => {
        this.notification.success('Cita completada');
        this.loadCitas();
        this.refreshService.triggerRefresh('citas');
      },
      error: (err: any) => this.notification.error(err.error?.error || 'Error al completar')
    });
  }

  agregarDisponibilidad(): void {
    if (!this.medicoId) {
      this.notification.error('Error: ID de médico no válido');
      return;
    }
    this.api.createDisponibilidad(this.medicoId, this.nuevaDisp).subscribe({
      next: () => {
        this.notification.success('Horario agregado correctamente');
        this.loadDisponibilidad();
        this.refreshService.triggerRefresh('disponibilidad');
        this.nuevaDisp = { dia_semana: '1', hora_inicio: '08:00', hora_fin: '17:00' };
      },
      error: (err: any) => this.notification.error(err.error?.error || 'Error al agregar horario')
    });
  }

  toggleDisponibilidad(d: any): void {
    this.api.updateDisponibilidad(d.id, { activo: !d.activo }).subscribe({
      next: () => {
        this.notification.success(d.activo ? 'Horario desactivado' : 'Horario activado');
        this.loadDisponibilidad();
        this.refreshService.triggerRefresh('disponibilidad');
      },
      error: (err: any) => this.notification.error(err.error?.error || 'Error al actualizar')
    });
  }

  getDiaNombre(dia: number): string {
    const dias = ['', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];
    return dias[dia] || '';
  }

  onPacienteChange(): void {
    this.nuevoHistorial.cita_id = null;
    this.citasPaciente = this.citas.filter(c =>
      c.paciente_id === Number(this.nuevoHistorial.paciente_id) &&
      c.estado === 'confirmada'
    );
  }

  getCitasPaciente(): any[] {
    return this.citasPaciente;
  }

  abrirModalHistorial(cita: any): void {
    this.citaSeleccionada = cita;
    this.nuevoHistorial = {
      paciente_id: cita.paciente_id,
      diagnostico: '',
      tratamiento: '',
      observaciones: '',
      cita_id: cita.id
    };
    this.citasPaciente = [cita];
    this.activeTab = 'historial';
  }

  registrarHistorial(): void {
    if (!this.nuevoHistorial.paciente_id || !this.nuevoHistorial.diagnostico) {
      this.notification.error('Por favor complete los campos requeridos');
      return;
    }

    this.loading = true;
    const historialData = {
      paciente_id: this.nuevoHistorial.paciente_id,
      diagnostico: this.nuevoHistorial.diagnostico,
      tratamiento: this.nuevoHistorial.tratamiento,
      observaciones: this.nuevoHistorial.observaciones,
      cita_id: this.nuevoHistorial.cita_id || null
    };

    this.api.createHistorial(historialData).subscribe({
      next: () => {
        this.notification.success('Historial médico registrado correctamente');
        this.nuevoHistorial = { paciente_id: '', diagnostico: '', tratamiento: '', observaciones: '', cita_id: null };
        this.loading = false;
        this.loadCitas();
        this.refreshService.triggerRefresh('citas');
      },
      error: (err: any) => {
        this.notification.error(err.error?.error || 'Error al registrar historial');
        this.loading = false;
      }
    });
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}