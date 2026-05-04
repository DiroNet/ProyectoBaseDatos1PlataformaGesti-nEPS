import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { ApiService } from '../../services/api.service';
import { DataRefreshService } from '../../services/data-refresh.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-dashboard-admin',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './dashboard-admin.component.html',
  styleUrls: ['./dashboard-admin.component.css']
})
export class DashboardAdminComponent implements OnInit, OnDestroy {
  activeTab = 'usuarios';
  filterFecha = '';
  filterMedico = '';
  filterEstado = '';
  usuarios: any[] = [];
  medicos: any[] = [];
  citas: any[] = [];
  especialidades: any[] = [];
  
  // Filtros
  searchTerm = '';
  filterRol = '';
  
  // Notificaciones
  showNotification = false;
  private refreshSub: Subscription | null = null;
  notificationType = '';
  notificationMessage = '';
  
  // Modal de eliminación
  showConfirmDelete = false;
  deleteTarget: any = null;
  deleteType: '' | 'usuario' | 'medico' = '';
  
  // Nuevo médico
  showAgregarMedico = false;
  nuevoMedico: any = { nombre: '', apellido: '', email: '', telefono: '', password: '', especialidad_id: '', cedula_profesional: '' };

  // Nueva especialidad
  showAgregarEspecialidad = false;
  nuevaEspecialidad: any = { nombre: '', descripcion: '' };

  constructor(
    private authService: AuthService, 
    private api: ApiService, 
    private router: Router,
    private refreshService: DataRefreshService
  ) {}

  ngOnInit(): void {
    const user = this.authService.getUser();
    if (!user || this.authService.getUserRole() !== 'administrador') {
      this.router.navigate(['/login']);
      return;
    }
    this.loadUsuarios();
    this.loadMedicos();
    this.loadCitas();
    this.loadEspecialidades();
    
    this.refreshSub = this.refreshService.refresh$.subscribe((type: string) => {
      if (type === 'usuarios' || type === 'all') this.loadUsuarios();
      if (type === 'citas' || type === 'all') this.loadCitas();
      if (type === 'medicos' || type === 'all') this.loadMedicos();
    });
  }

  ngOnDestroy(): void {
    this.refreshSub?.unsubscribe();
  }

  showNotify(message: string, type: string, duration = 3000): void {
    this.notificationMessage = message;
    this.notificationType = type;
    this.showNotification = true;
    setTimeout(() => this.showNotification = false, duration);
  }

  get filteredUsuarios(): any[] {
    return this.usuarios.filter(u => {
      const matchesSearch = !this.searchTerm || 
        u.nombre?.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        u.apellido?.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        u.email?.toLowerCase().includes(this.searchTerm.toLowerCase());
      
      const matchesRol = !this.filterRol || u.rol_nombre === this.filterRol;
      const matchesEstado = !this.filterEstado || 
        (this.filterEstado === 'activo' && u.activo) ||
        (this.filterEstado === 'inactivo' && !u.activo);
      
      return matchesSearch && matchesRol && matchesEstado;
    });
  }

  loadUsuarios(): void {
    this.api.getUsuarios().subscribe({
      next: (data: any) => this.usuarios = data,
      error: (err: any) => console.error(err)
    });
  }

  loadMedicos(): void {
    this.api.getMedicos().subscribe({
      next: (data: any) => this.medicos = data,
      error: (err: any) => console.error(err)
    });
  }

  loadCitas(): void {
    const filters: any = {};
    if (this.filterFecha) filters.fecha = this.filterFecha;
    if (this.filterMedico) filters.medico_id = Number(this.filterMedico);
    if (this.filterEstado) filters.estado = this.filterEstado;
    
    this.api.getCitas(filters).subscribe({
      next: (data: any) => this.citas = data,
      error: (err: any) => console.error(err)
    });
  }

  cambiarEstadoCita(cita: any, nuevoEstado: string): void {
    this.api.updateCita(cita.id, { estado: nuevoEstado }).subscribe({
      next: () => {
        cita.estado = nuevoEstado;
        this.showNotify(`Cita actualizada a ${nuevoEstado}`, 'success');
        this.refreshService.triggerRefresh('citas');
      },
      error: (err: any) => this.showNotify(err.error?.error || 'Error al actualizar cita', 'error')
    });
  }

  loadEspecialidades(): void {
    this.api.getEspecialidades().subscribe({
      next: (data: any) => this.especialidades = data,
      error: (err: any) => console.error(err)
    });
  }

  agregarEspecialidad(): void {
    this.api.createEspecialidad(this.nuevaEspecialidad).subscribe({
      next: () => {
        this.showNotify('Especialidad agregada correctamente', 'success');
        this.loadEspecialidades();
        this.showAgregarEspecialidad = false;
        this.nuevaEspecialidad = { nombre: '', descripcion: '' };
      },
      error: (err: any) => this.showNotify(err.error?.error || 'Error al agregar especialidad', 'error')
    });
  }

  toggleUsuario(usuario: any): void {
    const newEstado = !usuario.activo;
    this.api.updateUsuario(usuario.id, { 
      activo: newEstado,
      estado_id: newEstado ? 1 : 2  // 1 = activo, 2 = inactivo
    }).subscribe({
      next: () => {
        usuario.activo = newEstado;
        usuario.estado = newEstado ? 'activo' : 'inactivo';
        this.showNotify(`Usuario ${newEstado ? 'activado' : 'desactivado'} correctamente`, 'success');
        this.refreshService.triggerRefresh('usuarios');
      },
      error: (err: any) => this.showNotify(err.error?.error || 'Error al actualizar usuario', 'error')
    });
  }

  eliminarUsuario(usuario: any): void {
    this.deleteTarget = usuario;
    this.deleteType = 'usuario';
    this.showConfirmDelete = true;
  }

  confirmarEliminar(): void {
    if (!this.deleteTarget || !this.deleteType) return;
    
    if (this.deleteType === 'usuario') {
      this.api.deleteUsuario(this.deleteTarget.id).subscribe({
        next: () => {
          this.showNotify('Usuario eliminado correctamente', 'success');
          this.loadUsuarios();
          this.refreshService.triggerRefresh('usuarios');
        },
        error: (err: any) => this.showNotify(err.error?.error || 'Error al eliminar usuario', 'error')
      });
    } else if (this.deleteType === 'medico') {
      this.api.deleteMedico(this.deleteTarget.id).subscribe({
        next: () => {
          this.showNotify('Médico eliminado correctamente', 'success');
          this.loadMedicos();
          this.refreshService.triggerRefresh('medicos');
        },
        error: (err: any) => this.showNotify(err.error?.error || 'Error al eliminar médico', 'error')
      });
    }
    
    this.showConfirmDelete = false;
    this.deleteTarget = null;
    this.deleteType = '';
  }

  cancelarEliminar(): void {
    this.showConfirmDelete = false;
    this.deleteTarget = null;
    this.deleteType = '';
  }

  agregarMedico(): void {
    const espId = this.nuevoMedico.especialidad_id;
    const espSeleccionada = espId ? this.especialidades.find(e => String(e.id) === String(espId)) : null;
    const data = {
      nombre: this.nuevoMedico.nombre,
      apellido: this.nuevoMedico.apellido,
      email: this.nuevoMedico.email,
      telefono: this.nuevoMedico.telefono,
      password: this.nuevoMedico.password,
      especialidad: espSeleccionada?.nombre || '',
      especialidad_id: espId ? Number(espId) : null,
      cedula_profesional: this.nuevoMedico.cedula_profesional
    };
    this.api.createMedico(data).subscribe({
      next: () => {
        this.showNotify('Médico agregado correctamente', 'success');
        this.loadMedicos();
        this.loadUsuarios();
        this.refreshService.triggerRefresh('medicos');
        this.refreshService.triggerRefresh('usuarios');
        this.showAgregarMedico = false;
        this.nuevoMedico = { nombre: '', apellido: '', email: '', telefono: '', password: '', especialidad_id: '', cedula_profesional: '' };
      },
      error: (err: any) => this.showNotify(err.error?.error || 'Error al agregar médico', 'error')
    });
  }

  toggleMedico(medico: any): void {
    this.api.updateMedico(medico.id, { activo: !medico.activo }).subscribe({
      next: () => {
        medico.activo = !medico.activo;
        this.showNotify(`Médico ${medico.activo ? 'activado' : 'desactivado'} correctamente`, 'success');
        this.refreshService.triggerRefresh('medicos');
      },
      error: (err: any) => this.showNotify(err.error?.error || 'Error al actualizar médico', 'error')
    });
  }

  eliminarMedico(medico: any): void {
    this.deleteTarget = medico;
    this.deleteType = 'medico';
    this.showConfirmDelete = true;
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}