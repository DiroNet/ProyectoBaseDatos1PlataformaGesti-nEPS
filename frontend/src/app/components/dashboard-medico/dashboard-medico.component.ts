import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-dashboard-medico',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './dashboard-medico.component.html',
  styleUrls: ['./dashboard-medico.component.css']
})
export class DashboardMedicoComponent implements OnInit {
  user: any;
  medicoId = 0;
  activeTab = 'agenda';
  filterFecha = '';
  citas: any[] = [];
  disponibilidad: any[] = [];
  pacientes: any[] = [];
  loading = false;
  
  // Notificaciones
  showNotification = false;
  notificationType = '';
  notificationMessage = '';
  
  nuevaDisp: any = { dia_semana: '1', hora_inicio: '08:00', hora_fin: '17:00' };
  nuevoHistorial: any = { paciente_id: '', diagnostico: '', tratamiento: '', observaciones: '', cita_id: null };
  citasPaciente: any[] = [];

  constructor(private authService: AuthService, private api: ApiService, private router: Router) {}

  showNotify(message: string, type: string, duration = 3000): void {
    this.notificationMessage = message;
    this.notificationType = type;
    this.showNotification = true;
    setTimeout(() => this.showNotification = false, duration);
  }

  ngOnInit(): void {
    this.user = this.authService.getUser();
    if (!this.user || this.authService.getUserRole() !== 'medico') {
      this.router.navigate(['/login']);
      return;
    }
    this.medicoId = this.user.medico_id || 0;
    if (!this.medicoId) {
      this.showNotify('Error: No se encontró el ID del médico', 'error');
      return;
    }
    this.loadCitas();
    this.loadDisponibilidad();
    this.loadPacientes();
  }

  loadCitas(): void {
    const filters: any = { medico_id: this.medicoId };
    if (this.filterFecha) filters.fecha = this.filterFecha;
    
    this.api.getCitas(filters).subscribe({
      next: (data: any) => this.citas = data,
      error: (err: any) => console.error(err)
    });
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

  confirmarCita(id: number): void {
    this.api.updateCita(id, { estado: 'confirmada' }).subscribe({
      next: () => {
        this.showNotify('Cita confirmada', 'success');
        this.loadCitas();
      },
      error: (err: any) => this.showNotify(err.error?.error || 'Error al confirmar', 'error')
    });
  }

  rechazarCita(id: number): void {
    this.api.updateCita(id, { estado: 'cancelada' }).subscribe({
      next: () => {
        this.showNotify('Cita cancelada', 'success');
        this.loadCitas();
      },
      error: (err: any) => this.showNotify(err.error?.error || 'Error al cancelar', 'error')
    });
  }

  completarCita(id: number): void {
    this.api.updateCita(id, { estado: 'completada' }).subscribe({
      next: () => {
        this.showNotify('Cita completada', 'success');
        this.loadCitas();
      },
      error: (err: any) => this.showNotify(err.error?.error || 'Error al completar', 'error')
    });
  }

  agregarDisponibilidad(): void {
    if (!this.medicoId) {
      this.showNotify('Error: ID de médico no válido', 'error');
      return;
    }
    this.api.createDisponibilidad(this.medicoId, this.nuevaDisp).subscribe({
      next: () => {
        this.showNotify('Horario agregado correctamente', 'success');
        this.loadDisponibilidad();
        this.nuevaDisp = { dia_semana: '1', hora_inicio: '08:00', hora_fin: '17:00' };
      },
      error: (err: any) => this.showNotify(err.error?.error || 'Error al agregar horario', 'error')
    });
  }

  toggleDisponibilidad(d: any): void {
    this.api.updateDisponibilidad(d.id, { activo: !d.activo }).subscribe({
      next: () => {
        this.showNotify(d.activo ? 'Horario desactivado' : 'Horario activado', 'success');
        this.loadDisponibilidad();
      },
      error: (err: any) => this.showNotify(err.error?.error || 'Error al actualizar', 'error')
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
      (c.estado === 'pendiente' || c.estado === 'confirmada')
    );
  }

  getCitasPaciente(): any[] {
    return this.citasPaciente;
  }

  registrarHistorial(): void {
    if (!this.nuevoHistorial.paciente_id || !this.nuevoHistorial.diagnostico) {
      this.showNotify('Por favor complete los campos requeridos', 'error');
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
        this.showNotify('Historial médico registrado correctamente', 'success');
        this.nuevoHistorial = { paciente_id: '', diagnostico: '', tratamiento: '', observaciones: '', cita_id: null };
        this.loading = false;
        this.loadCitas();
      },
      error: (err: any) => {
        this.showNotify(err.error?.error || 'Error al registrar historial', 'error');
        this.loading = false;
      }
    });
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}