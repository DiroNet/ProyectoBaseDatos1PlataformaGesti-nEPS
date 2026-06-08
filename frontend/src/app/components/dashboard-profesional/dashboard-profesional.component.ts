import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { ApiService } from '../../services/api.service';
import { NotificationService } from '../../services/notification.service';
import { RealtimeService } from '../../services/realtime.service';

@Component({
  selector: 'app-dashboard-profesional',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './dashboard-profesional.component.html',
  styleUrl: './dashboard-profesional.component.css'
})
export class DashboardProfesionalComponent implements OnInit, OnDestroy {
  user: any;
  profesionalId: number = 0;
  activeTab = 'citas';
  citas: any[] = [];
  historial: any[] = [];
  disponibilidad: any[] = [];
  loading = false;
  initialLoading = true;

  nuevoHistorial: any = { id_afiliado: '', diagnostico: '', tratamiento: '', id_cita: '' };
  afiliados: any[] = [];

  nuevaDisp: any = { dia_semana: 1, hora_inicio: '08:00', hora_fin: '17:00' };

  diasSemana = ['', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];

  constructor(
    private authService: AuthService,
    private api: ApiService,
    private router: Router,
    private notification: NotificationService,
    private realtime: RealtimeService
  ) {}

  ngOnInit(): void {
    this.user = this.authService.getUser();
    if (!this.user || this.authService.getUserRole() !== 'PROFESIONAL') {
      this.router.navigate(['/login']);
      return;
    }
    this.loadData();
    this.startRealtimeUpdates();
  }

  ngOnDestroy(): void {
    this.realtime.stopAllPolling();
  }

  startRealtimeUpdates(): void {
    this.realtime.startPolling('profesional-citas', () => this.loadCitasSilent());
    this.realtime.startPolling('profesional-disponibilidad', () => this.loadDisponibilidadSilent());
  }

  loadData(): void {
    this.initialLoading = true;
    Promise.all([
      this.loadCitasPromise(),
      this.loadAfiliadosPromise()
    ]).then(() => {
      this.loadProfesionalId();
    }).catch(() => {
      this.initialLoading = false;
    });
  }

  loadCitasPromise(): Promise<void> {
    return new Promise((resolve) => {
      this.api.getCitas().subscribe({
        next: (data: any) => { this.citas = data; resolve(); },
        error: () => resolve()
      });
    });
  }

  loadAfiliadosPromise(): Promise<void> {
    return new Promise((resolve) => {
      this.api.getAfiliados().subscribe({
        next: (data: any) => { this.afiliados = data; resolve(); },
        error: () => resolve()
      });
    });
  }

  loadHistorialPromise(): Promise<void> {
    return new Promise((resolve) => {
      this.api.getHistorial().subscribe({
        next: (data: any) => { this.historial = data; resolve(); },
        error: () => resolve()
      });
    });
  }

  loadProfesionalId(): void {
    this.api.getProfesionales().subscribe({
      next: (data: any) => {
        const prof = data.find((p: any) => p.usuario?.email === this.user?.email);
        if (prof) {
          this.profesionalId = prof.id_profesional;
          this.loadDisponibilidad();
        }
        this.initialLoading = false;
      },
      error: (err: any) => {
        console.error(err);
        this.initialLoading = false;
      }
    });
  }

  loadCitas(): void {
    this.api.getCitas().subscribe({
      next: (data: any) => this.citas = data,
      error: (err: any) => console.error(err)
    });
  }

  loadCitasSilent(): void {
    this.api.getCitas().subscribe({
      next: (data: any) => this.citas = data,
      error: () => {}
    });
  }

  loadHistorial(): void {
    this.api.getHistorial().subscribe({
      next: (data: any) => this.historial = data,
      error: (err: any) => console.error(err)
    });
  }

  loadAfiliados(): void {
    this.api.getAfiliados().subscribe({
      next: (data: any) => this.afiliados = data,
      error: (err: any) => console.error(err)
    });
  }

  loadDisponibilidad(): void {
    if (this.profesionalId) {
      this.api.getDisponibilidad(this.profesionalId).subscribe({
        next: (data: any) => this.disponibilidad = data,
        error: (err: any) => console.error(err)
      });
    }
  }

  loadDisponibilidadSilent(): void {
    if (this.profesionalId) {
      this.api.getDisponibilidad(this.profesionalId).subscribe({
        next: (data: any) => this.disponibilidad = data,
        error: () => {}
      });
    }
  }

  getDiaSemana(dia: number): string {
    return this.diasSemana[dia] || '';
  }

  agregarDisponibilidad(): void {
    if (!this.profesionalId) {
      this.notification.error('Error al identificar profesional');
      return;
    }
    if (!this.nuevaDisp.hora_inicio || !this.nuevaDisp.hora_fin) {
      this.notification.error('Complete los horarios');
      return;
    }

    this.loading = true;
    this.api.createDisponibilidad({
      id_profesional: this.profesionalId,
      dia_semana: this.nuevaDisp.dia_semana,
      hora_inicio: this.nuevaDisp.hora_inicio,
      hora_fin: this.nuevaDisp.hora_fin
    }).subscribe({
      next: () => {
        this.notification.success('Disponibilidad agregada');
        this.loading = false;
        this.nuevaDisp = { dia_semana: 1, hora_inicio: '08:00', hora_fin: '17:00' };
        this.loadDisponibilidad();
      },
      error: (err: any) => {
        this.notification.error(err.error?.error || 'Error al agregar');
        this.loading = false;
      }
    });
  }

  eliminarDisponibilidad(id: number): void {
    this.notification.confirmDanger('¿Está seguro de eliminar este horario?', () => {
      this.api.deleteDisponibilidad(id).subscribe({
        next: () => {
          this.notification.success('Horario eliminado');
          this.loadDisponibilidad();
        },
        error: (err: any) => this.notification.error(err.error?.error || 'Error')
      });
    });
  }

  actualizarEstado(cita: any, nuevoEstado: string): void {
    this.api.updateCita(cita.id_cita, { estado: nuevoEstado }).subscribe({
      next: () => {
        this.notification.success('Cita ' + nuevoEstado.toLowerCase());
        this.loadCitas();
      },
      error: (err: any) => this.notification.error(err.error?.error || 'Error')
    });
  }

  registrarHistorial(): void {
    if (!this.nuevoHistorial.id_afiliado || !this.nuevoHistorial.diagnostico) {
      this.notification.error('Complete los campos requeridos');
      return;
    }

    this.loading = true;
    this.api.createHistorial(this.nuevoHistorial).subscribe({
      next: () => {
        this.notification.success('Historial registrado exitosamente');
        this.loading = false;
        this.nuevoHistorial = { id_afiliado: '', diagnostico: '', tratamiento: '', id_cita: '' };
        this.loadHistorial();
        this.activeTab = 'historial';
      },
      error: (err: any) => {
        this.notification.error(err.error?.error || 'Error al registrar');
        this.loading = false;
      }
    });
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}