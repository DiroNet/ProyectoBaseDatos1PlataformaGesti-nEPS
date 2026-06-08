import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { ApiService } from '../../services/api.service';
import { NotificationService } from '../../services/notification.service';
import { RealtimeService } from '../../services/realtime.service';

@Component({
  selector: 'app-dashboard-afiliado',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './dashboard-afiliado.component.html',
  styleUrl: './dashboard-afiliado.component.css'
})
export class DashboardAfiliadoComponent implements OnInit, OnDestroy {
  user: any;
  activeTab = 'citas';
  citas: any[] = [];
  profesionales: any[] = [];
  centros: any[] = [];
  historial: any[] = [];
  facturas: any[] = [];
  loading = false;
  initialLoading = true;

  disponibilidad: any[] = [];
  horasDisponibles: string[] = [];

  nuevaCita: any = { id_profesional: '', id_centro: '', fecha: '', hora: '' };
  minDate = new Date().toISOString().split('T')[0];

  constructor(
    private authService: AuthService,
    private api: ApiService,
    private router: Router,
    private notification: NotificationService,
    private realtime: RealtimeService
  ) {}

  ngOnInit(): void {
    this.user = this.authService.getUser();
    if (!this.user || this.authService.getUserRole() !== 'AFILIADO') {
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
    this.realtime.startPolling('afiliado-citas', () => this.loadCitasSilent());
    this.realtime.startPolling('afiliado-historial', () => this.loadHistorialSilent());
    this.realtime.startPolling('afiliado-facturas', () => this.loadFacturasSilent());
  }

  loadData(): void {
    this.initialLoading = true;
    Promise.all([
      this.loadCitasPromise(),
      this.loadProfesionalesPromise(),
      this.loadCentrosPromise()
    ]).then(() => {
      this.initialLoading = false;
    }).catch(() => {
      this.initialLoading = false;
    });
  }

  loadCitasPromise(): Promise<void> {
    return new Promise((resolve) => {
      this.api.getCitasProximas().subscribe({
        next: (data: any) => { this.citas = data; resolve(); },
        error: () => resolve()
      });
    });
  }

  loadProfesionalesPromise(): Promise<void> {
    return new Promise((resolve) => {
      this.api.getProfesionales().subscribe({
        next: (data: any) => { this.profesionales = data; resolve(); },
        error: () => resolve()
      });
    });
  }

  loadCentrosPromise(): Promise<void> {
    return new Promise((resolve) => {
      this.api.getCentros().subscribe({
        next: (data: any) => { this.centros = data; resolve(); },
        error: () => resolve()
      });
    });
  }

  loadCitas(): void {
    this.loading = true;
    this.api.getCitasProximas().subscribe({
      next: (data: any) => { this.citas = data; this.loading = false; },
      error: () => { this.loading = false; }
    });
  }

  loadCitasSilent(): void {
    this.api.getCitasProximas().subscribe({
      next: (data: any) => this.citas = data,
      error: () => {}
    });
  }

  loadProfesionales(): void {
    this.api.getProfesionales().subscribe({
      next: (data: any) => this.profesionales = data,
      error: (err: any) => console.error(err)
    });
  }

  loadCentros(): void {
    this.api.getCentros().subscribe({
      next: (data: any) => this.centros = data,
      error: (err: any) => console.error(err)
    });
  }

  loadHistorial(): void {
    this.loading = true;
    this.api.getHistorial().subscribe({
      next: (data: any) => { this.historial = data; this.loading = false; },
      error: () => { this.loading = false; }
    });
  }

  loadHistorialSilent(): void {
    this.api.getHistorial().subscribe({
      next: (data: any) => this.historial = data,
      error: () => {}
    });
  }

  loadFacturas(): void {
    this.loading = true;
    this.api.getFacturas().subscribe({
      next: (data: any) => { this.facturas = data; this.loading = false; },
      error: () => { this.loading = false; }
    });
  }

  loadFacturasSilent(): void {
    this.api.getFacturas().subscribe({
      next: (data: any) => this.facturas = data,
      error: () => {}
    });
  }

  onProfesionalChange(): void {
    if (this.nuevaCita.id_profesional) {
      this.api.getDisponibilidad(this.nuevaCita.id_profesional).subscribe({
        next: (data: any) => {
          this.disponibilidad = data;
          this.horasDisponibles = this.generarHorasDisponibles(data);
        },
        error: (err: any) => {
          console.error(err);
          this.disponibilidad = [];
          this.horasDisponibles = [];
        }
      });
    } else {
      this.disponibilidad = [];
      this.horasDisponibles = [];
    }
    this.nuevaCita.hora = '';
  }

  generarHorasDisponibles(disp: any[]): string[] {
    const horas: string[] = [];
    disp.forEach(d => {
      const inicio = this.horaToMinutes(d.hora_inicio);
      const fin = this.horaToMinutes(d.hora_fin);
      for (let m = inicio; m < fin; m += 60) {
        horas.push(this.minutesToTime(m));
      }
    });
    return horas.sort();
  }

  horaToMinutes(hora: string): number {
    const [h, m] = hora.split(':').map(Number);
    return h * 60 + m;
  }

  minutesToTime(minutes: number): string {
    const h = Math.floor(minutes / 60);
    const m = minutes % 60;
    return (h < 10 ? '0' : '') + h + ':' + (m < 10 ? '0' : '') + m;
  }

  agendarCita(): void {
    if (!this.nuevaCita.id_profesional || !this.nuevaCita.id_centro || !this.nuevaCita.fecha || !this.nuevaCita.hora) {
      this.notification.error('Todos los campos son requeridos');
      return;
    }

    this.loading = true;
    const fechaCompleta = this.nuevaCita.fecha + ' ' + this.nuevaCita.hora;

    this.api.createCita({
      id_profesional: this.nuevaCita.id_profesional,
      id_centro: this.nuevaCita.id_centro,
      fecha: fechaCompleta
    }).subscribe({
      next: () => {
        this.notification.success('Cita agendada exitosamente');
        this.loading = false;
        this.nuevaCita = { id_profesional: '', id_centro: '', fecha: '', hora: '' };
        this.disponibilidad = [];
        this.horasDisponibles = [];
        this.loadCitas();
        this.activeTab = 'citas';
      },
      error: (err: any) => {
        this.notification.error(err.error?.error || 'Error al agendar cita');
        this.loading = false;
      }
    });
  }

  cancelarCita(cita: any): void {
    this.notification.confirmDanger('¿Está seguro de cancelar esta cita?', () => {
      this.api.deleteCita(cita.id_cita).subscribe({
        next: () => {
          this.notification.success('Cita cancelada correctamente');
          this.loadCitas();
        },
        error: (err: any) => this.notification.error(err.error?.error || 'Error al cancelar')
      });
    });
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}