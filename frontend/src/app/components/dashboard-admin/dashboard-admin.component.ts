import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { ApiService } from '../../services/api.service';
import { NotificationService } from '../../services/notification.service';
import { RealtimeService } from '../../services/realtime.service';

@Component({
  selector: 'app-dashboard-admin',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './dashboard-admin.component.html',
  styleUrl: './dashboard-admin.component.css'
})
export class DashboardAdminComponent implements OnInit, OnDestroy {
  user: any;
  activeTab = 'dashboard';
  loading = false;
  initialLoading = true;

  afiliados: any[] = [];
  profesionales: any[] = [];
  centros: any[] = [];
  planes: any[] = [];
  citas: any[] = [];
  facturas: any[] = [];

  facturasPendientes: any[] = [];
  facturacionPlan: any[] = [];
  diagnosticosFrecuentes: any[] = [];
  centrosUtilizados: any[] = [];

  filterYear = new Date().getFullYear();
  filterPlan: number | null = null;
  filterCentro: number | null = null;

  maxFecha = new Date().toISOString().split('T')[0];
  nuevoAfiliado: any = { email: '', password: '', nombre: '', documento: '', telefono: '', direccion: '', fecha_nacimiento: '', id_plan: null };
  nuevoProfesional: any = { email: '', password: '', nombre: '', especialidad: '', id_centro: null };
  nuevoCentro: any = { nombre: '', direccion: '', ciudad: '' };
  nuevaFactura: any = { id_afiliado: '', total: 0 };
  nuevoPlan: any = { nombre: '', descripcion: '', costo: 0 };
  editandoPlan = false;
  editandoCentro = false;

  constructor(
    private authService: AuthService,
    private api: ApiService,
    private router: Router,
    private notification: NotificationService,
    private realtime: RealtimeService
  ) {}

  ngOnInit(): void {
    this.user = this.authService.getUser();
    if (!this.user || this.authService.getUserRole() !== 'ADMIN') {
      this.router.navigate(['/login']);
      return;
    }
    this.loadData();
    this.initDatabase();
  }

  ngOnDestroy(): void {
    this.realtime.stopAllPolling();
  }

  startRealtimeUpdates(): void {
    this.realtime.startPolling('admin-afiliados', () => this.loadAfiliadosSilent());
    this.realtime.startPolling('admin-profesionales', () => this.loadProfesionalesSilent());
    this.realtime.startPolling('admin-centros', () => this.loadCentrosSilent());
    this.realtime.startPolling('admin-planes', () => this.loadPlanesSilent());
    this.realtime.startPolling('admin-citas', () => this.loadCitasSilent());
    this.realtime.startPolling('admin-facturas', () => this.loadFacturasSilent());
  }

  initDatabase(): void {
    this.api.initDB().subscribe({
      next: () => console.log('Base de datos inicializada'),
      error: (err: any) => console.error(err)
    });
  }

  loadData(): void {
    this.initialLoading = true;
    Promise.all([
      this.loadAfiliadosPromise(),
      this.loadProfesionalesPromise(),
      this.loadCentrosPromise(),
      this.loadPlanesPromise(),
      this.loadCitasPromise(),
      this.loadFacturasPromise()
    ]).then(() => {
      this.initialLoading = false;
      this.loadConsultas();
    }).catch(() => {
      this.initialLoading = false;
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

  loadPlanesPromise(): Promise<void> {
    return new Promise((resolve) => {
      this.api.getPlanes().subscribe({
        next: (data: any) => { this.planes = data; resolve(); },
        error: () => resolve()
      });
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

  loadFacturasPromise(): Promise<void> {
    return new Promise((resolve) => {
      this.api.getFacturas().subscribe({
        next: (data: any) => { this.facturas = data; resolve(); },
        error: () => resolve()
      });
    });
  }

  loadAfiliadosSilent(): void {
    this.api.getAfiliados().subscribe({
      next: (data: any) => this.afiliados = data,
      error: () => {}
    });
  }

  loadProfesionalesSilent(): void {
    this.api.getProfesionales().subscribe({
      next: (data: any) => this.profesionales = data,
      error: () => {}
    });
  }

  loadCentrosSilent(): void {
    this.api.getCentros().subscribe({
      next: (data: any) => this.centros = data,
      error: () => {}
    });
  }

  loadPlanesSilent(): void {
    this.api.getPlanes().subscribe({
      next: (data: any) => this.planes = data,
      error: () => {}
    });
  }

  loadCitasSilent(): void {
    this.api.getCitas().subscribe({
      next: (data: any) => this.citas = data,
      error: () => {}
    });
  }

  loadFacturasSilent(): void {
    this.api.getFacturas().subscribe({
      next: (data: any) => this.facturas = data,
      error: () => {}
    });
  }

  loadConsultas(): void {
    this.api.getAfiliadosFacturasPendientes().subscribe({
      next: (data: any) => this.facturasPendientes = data,
      error: (err: any) => console.error(err)
    });
    this.api.getFacturacionPorPlan().subscribe({
      next: (data: any) => this.facturacionPlan = data,
      error: (err: any) => console.error(err)
    });
    this.api.getDiagnosticosFrecuentes().subscribe({
      next: (data: any) => this.diagnosticosFrecuentes = data,
      error: (err: any) => console.error(err)
    });
    this.api.getCentrosMasUtilizados().subscribe({
      next: (data: any) => this.centrosUtilizados = data,
      error: (err: any) => console.error(err)
    });
  }

  filtrarNumerosAdmin(event: any, obj: any, campo: string): void {
    const valor = event.target.value.replace(/\D/g, '');
    obj[campo] = valor;
    event.target.value = valor;
  }

  crearAfiliado(): void {
    const a = this.nuevoAfiliado;

    if (!a.nombre?.trim()) {
      this.notification.error('El nombre es requerido');
      return;
    }

    if (!a.email?.trim()) {
      this.notification.error('El correo electrónico es requerido');
      return;
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(a.email)) {
      this.notification.error('Ingrese un correo electrónico válido');
      return;
    }

    if (!a.documento) {
      this.notification.error('El número de cédula es requerido');
      return;
    }
    if (a.documento.length < 6 || a.documento.length > 10) {
      this.notification.error('La cédula debe tener entre 6 y 10 dígitos');
      return;
    }

    if (!a.telefono) {
      this.notification.error('El teléfono celular es requerido');
      return;
    }
    if (!/^3\d{9}$/.test(a.telefono)) {
      this.notification.error('El teléfono debe ser un número móvil colombiano (10 dígitos, empieza con 3)');
      return;
    }

    if (!a.fecha_nacimiento) {
      this.notification.error('La fecha de nacimiento es requerida');
      return;
    }
    if (a.fecha_nacimiento > this.maxFecha) {
      this.notification.error('La fecha de nacimiento no puede ser una fecha futura');
      return;
    }

    if (!a.password) {
      this.notification.error('La contraseña es requerida');
      return;
    }
    if (a.password.length < 6) {
      this.notification.error('La contraseña debe tener al menos 6 caracteres');
      return;
    }

    this.loading = true;
    this.api.createAfiliado(a).subscribe({
      next: () => {
        this.notification.success('Afiliado creado exitosamente');
        this.loading = false;
        this.nuevoAfiliado = { email: '', password: '', nombre: '', documento: '', telefono: '', direccion: '', fecha_nacimiento: '', id_plan: null };
        this.loadAfiliadosSilent();
      },
      error: (err: any) => {
        this.notification.error(err.error?.error || 'Error al crear');
        this.loading = false;
      }
    });
  }

  crearProfesional(): void {
    if (!this.nuevoProfesional.email || !this.nuevoProfesional.password || !this.nuevoProfesional.nombre) {
      this.notification.error('Complete los campos requeridos');
      return;
    }
    this.loading = true;
    this.api.createProfesional(this.nuevoProfesional).subscribe({
      next: () => {
        this.notification.success('Profesional creado exitosamente');
        this.loading = false;
        this.nuevoProfesional = { email: '', password: '', nombre: '', especialidad: '', id_centro: null };
        this.loadProfesionalesSilent();
      },
      error: (err: any) => {
        this.notification.error(err.error?.error || 'Error al crear');
        this.loading = false;
      }
    });
  }

  crearCentro(): void {
    if (!this.nuevoCentro.nombre) {
      this.notification.error('Ingrese el Nombre del centro');
      return;
    }
    this.loading = true;
    if (this.editandoCentro) {
      this.api.updateCentro(this.nuevoCentro.id, this.nuevoCentro).subscribe({
        next: () => {
          this.notification.success('Centro actualizado');
          this.loading = false;
          this.nuevoCentro = { nombre: '', direccion: '', ciudad: '' };
          this.editandoCentro = false;
          this.loadCentrosSilent();
        },
        error: (err: any) => {
          this.notification.error(err.error?.error || 'Error al actualizar');
          this.loading = false;
        }
      });
    } else {
      this.api.createCentro(this.nuevoCentro).subscribe({
        next: () => {
          this.notification.success('Centro creado exitosamente');
          this.loading = false;
          this.nuevoCentro = { nombre: '', direccion: '', ciudad: '' };
          this.loadCentrosSilent();
        },
        error: (err: any) => {
          this.notification.error(err.error?.error || 'Error al crear');
          this.loading = false;
        }
      });
    }
  }

  crearFactura(): void {
    if (!this.nuevaFactura.id_afiliado || !this.nuevaFactura.total) {
      this.notification.error('Complete los campos requeridos');
      return;
    }
    this.loading = true;
    this.api.createFactura(this.nuevaFactura).subscribe({
      next: () => {
        this.notification.success('Factura creada exitosamente');
        this.loading = false;
        this.nuevaFactura = { id_afiliado: '', total: 0 };
        this.loadFacturasSilent();
      },
      error: (err: any) => {
        this.notification.error(err.error?.error || 'Error al crear');
        this.loading = false;
      }
    });
  }

  pagarFactura(factura: any): void {
    this.api.pagarFactura(factura.id_factura, 'Efectivo').subscribe({
      next: () => {
        this.notification.success('Factura pagada');
        this.loadFacturasSilent();
      },
      error: (err: any) => this.notification.error(err.error?.error || 'Error')
    });
  }

  eliminarFactura(id: number): void {
    this.notification.confirmDanger('¿Está seguro de eliminar esta factura?', () => {
      this.api.deleteFactura(id).subscribe({
        next: () => {
          this.notification.success('Factura eliminada');
          this.loadFacturasSilent();
        },
        error: (err: any) => this.notification.error(err.error?.error || 'Error al eliminar')
      });
    });
  }

  guardarPlan(): void {
    if (!this.nuevoPlan.nombre || !this.nuevoPlan.costo) {
      this.notification.error('Complete los campos requeridos');
      return;
    }
    this.loading = true;
    if (this.editandoPlan) {
      this.api.updatePlan(this.nuevoPlan.id, this.nuevoPlan).subscribe({
        next: () => {
          this.notification.success('Plan actualizado');
          this.loading = false;
          this.nuevoPlan = { nombre: '', descripcion: '', costo: 0 };
          this.editandoPlan = false;
          this.loadPlanesSilent();
        },
        error: (err: any) => {
          this.notification.error(err.error?.error || 'Error al actualizar');
          this.loading = false;
        }
      });
    } else {
      this.api.createPlan(this.nuevoPlan).subscribe({
        next: () => {
          this.notification.success('Plan creado exitosamente');
          this.loading = false;
          this.nuevoPlan = { nombre: '', descripcion: '', costo: 0 };
          this.loadPlanesSilent();
        },
        error: (err: any) => {
          this.notification.error(err.error?.error || 'Error al crear');
          this.loading = false;
        }
      });
    }
  }

  editarPlan(plan: any): void {
    this.nuevoPlan = { id: plan.id_plan, nombre: plan.nombre, descripcion: plan.descripcion, costo: plan.costo };
    this.editandoPlan = true;
  }

  eliminarPlan(id: number): void {
    this.notification.confirmDanger('¿Está seguro de eliminar este plan?', () => {
      this.api.deletePlan(id).subscribe({
        next: () => {
          this.notification.success('Plan eliminado');
          this.loadPlanesSilent();
        },
        error: (err: any) => this.notification.error(err.error?.error || 'Error al eliminar')
      });
    });
  }

  cancelarEdicionPlan(): void {
    this.nuevoPlan = { nombre: '', descripcion: '', costo: 0 };
    this.editandoPlan = false;
  }

  editarCentro(centro: any): void {
    this.nuevoCentro = { id: centro.id_centro, nombre: centro.nombre, direccion: centro.direccion, ciudad: centro.ciudad };
    this.editandoCentro = true;
  }

  eliminarCentro(id: number): void {
    this.notification.confirmDanger('¿Está seguro de eliminar este centro?', () => {
      this.api.deleteCentro(id).subscribe({
        next: () => {
          this.notification.success('Centro eliminado');
          this.loadCentrosSilent();
        },
        error: (err: any) => this.notification.error(err.error?.error || 'Error al eliminar')
      });
    });
  }

  cancelarEdicionCentro(): void {
    this.editandoCentro = false;
    this.nuevoCentro = { nombre: '', direccion: '', ciudad: '' };
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}