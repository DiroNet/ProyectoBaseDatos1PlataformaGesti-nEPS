import { Component, OnInit, OnDestroy, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { Chart, registerables } from 'chart.js';
import { AuthService } from '../../services/auth.service';
import { ApiService } from '../../services/api.service';
import { NotificationService } from '../../services/notification.service';
import { RealtimeService } from '../../services/realtime.service';

Chart.register(...registerables);

@Component({
  selector: 'app-dashboard-admin',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './dashboard-admin.component.html',
  styleUrl: './dashboard-admin.component.css'
})
export class DashboardAdminComponent implements OnInit, AfterViewInit, OnDestroy {
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

  estadisticas: any = {
    totales: { afiliados: 0, profesionales: 0, centros: 0, citas: 0, facturas: 0 },
    citas_por_estado: { pendiente: 0, confirmada: 0, finalizada: 0, cancelada: 0 },
    facturas_por_estado: { pendiente: 0, pagada: 0 },
    afiliados_por_plan: [],
    citas_mes_actual: 0,
    facturacion: { total: 0, pendiente: 0 }
  };

  charts: any = {
    afiliadosPlan: null,
    citasEstado: null,
    facturacionPlan: null,
    centrosUtilizados: null,
    facturas: null
  };

  maxFecha = new Date().toISOString().split('T')[0];
  nuevoAfiliado: any = { email: '', password: '', nombre: '', tipo_documento: '', documento: '', telefono: '', direccion: '', fecha_nacimiento: '', id_plan: null };
  nuevoProfesional: any = { email: '', password: '', nombre: '', especialidad: '', id_centro: null };
  nuevoCentro: any = { nombre: '', direccion: '', ciudad: '' };
  nuevaFactura: any = { id_afiliado: '', total: 0 };
  nuevoPlan: any = { nombre: '', descripcion: '', costo: 0 };
  editandoPlan = false;
  editandoCentro = false;

  // Afiliado editar/ver
  editandoAfiliado = false;
  afiliadoEditar: any = {};
  afiliadoVer: any = null;

  // Profesional editar/ver
  editandoProfesional = false;
  profesionalEditar: any = {};
  profesionalVer: any = null;

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

  ngAfterViewInit(): void {
    if (!this.initialLoading) {
      this.initCharts();
    }
  }

  ngOnDestroy(): void {
    this.realtime.stopAllPolling();
    Object.values(this.charts).forEach((chart: any) => {
      if (chart) chart.destroy();
    });
  }

  onTabChange(tab: string): void {
    this.activeTab = tab;
    if (tab === 'dashboard') {
      setTimeout(() => this.initCharts(), 50);
    }
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
      this.loadFacturasPromise(),
      this.loadEstadisticasPromise()
    ]).then(() => {
      this.initialLoading = false;
      this.loadConsultas();
      setTimeout(() => this.initCharts(), 200);
    }).catch(() => {
      this.initialLoading = false;
    });
  }

  loadEstadisticasPromise(): Promise<void> {
    return new Promise((resolve) => {
      this.api.getDashboardEstadisticas().subscribe({
        next: (data: any) => { this.estadisticas = data; resolve(); },
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

  loadConsultas(): void {
    this.api.getAfiliadosFacturasPendientes().subscribe({
      next: (data: any) => this.facturasPendientes = data,
      error: () => {}
    });
    this.api.getFacturacionPorPlan().subscribe({
      next: (data: any) => this.facturacionPlan = data,
      error: () => {}
    });
    this.api.getDiagnosticosFrecuentes().subscribe({
      next: (data: any) => this.diagnosticosFrecuentes = data,
      error: () => {}
    });
    this.api.getCentrosMasUtilizados().subscribe({
      next: (data: any) => this.centrosUtilizados = data,
      error: () => {}
    });
  }

  initCharts(): void {
    Object.values(this.charts).forEach((chart: any) => {
      if (chart) chart.destroy();
    });
    this.createAfiliadosPorPlanChart();
    this.createCitasEstadoChart();
    this.createFacturacionChart();
    this.createCentrosChart();
    this.createFacturasChart();
  }

  createAfiliadosPorPlanChart(): void {
    const ctx = document.getElementById('afiliadosPlanChart') as HTMLCanvasElement;
    if (!ctx) return;
    
    if (this.charts.afiliadosPlan) {
      this.charts.afiliadosPlan.destroy();
    }

    const data = this.estadisticas.afiliados_por_plan || [];
    const labels = data.map((d: any) => d.plan);
    const values = data.map((d: any) => d.cantidad);

    this.charts.afiliadosPlan = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: labels.length ? labels : ['Sin datos'],
        datasets: [{
          data: values.length ? values : [1],
          backgroundColor: ['#0369a1', '#0ea5e9', '#06b6d4', '#14b8a6', '#22c55e'],
          borderWidth: 3,
          borderColor: '#fff',
          hoverOffset: 10
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '60%',
        plugins: {
          legend: { 
            position: 'right', 
            labels: { 
              color: '#1E293B',
              padding: 20,
              font: { size: 13, weight: 500 },
              usePointStyle: true,
              pointStyle: 'circle'
            } 
          }
        }
      }
    });
  }

  createCitasEstadoChart(): void {
    const ctx = document.getElementById('citasEstadoChart') as HTMLCanvasElement;
    if (!ctx) return;
    
    if (this.charts.citasEstado) {
      this.charts.citasEstado.destroy();
    }

    const estado = this.estadisticas.citas_por_estado || {};

    this.charts.citasEstado = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Pendiente', 'Confirmada', 'Finalizada', 'Cancelada'],
        datasets: [{
          data: [estado.pendiente || 0, estado.confirmada || 0, estado.finalizada || 0, estado.cancelada || 0],
          backgroundColor: ['#f59e0b', '#0d6efd', '#22c55e', '#ef4444'],
          borderWidth: 3,
          borderColor: '#fff',
          hoverOffset: 10
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '60%',
        plugins: {
          legend: { 
            position: 'right', 
            labels: { 
              color: '#1E293B',
              padding: 20,
              font: { size: 13, weight: 500 },
              usePointStyle: true,
              pointStyle: 'circle'
            } 
          }
        }
      }
    });
  }

  createFacturacionChart(): void {
    const ctx = document.getElementById('facturacionChart') as HTMLCanvasElement;
    if (!ctx) return;
    
    if (this.charts.facturacionPlan) {
      this.charts.facturacionPlan.destroy();
    }

    const data = this.facturacionPlan || [];
    const labels = data.map((d: any) => d.plan);
    const values = data.map((d: any) => d.facturacion_total);

    this.charts.facturacionPlan = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels.length ? labels : ['Sin datos'],
        datasets: [{
          label: 'Facturación ($)',
          data: values.length ? values : [0],
          backgroundColor: 'rgba(3, 105, 161, 0.1)',
          borderColor: '#0369a1',
          borderWidth: 3,
          fill: true,
          tension: 0.4,
          pointBackgroundColor: '#0369a1',
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          pointRadius: 6,
          pointHoverRadius: 8
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: { 
            beginAtZero: true, 
            ticks: { color: '#64748B', font: { size: 12 } },
            grid: { color: 'rgba(0,0,0,0.05)' }
          },
          x: { 
            ticks: { color: '#64748B', font: { size: 12 } },
            grid: { display: false }
          }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  }

  createCentrosChart(): void {
    const ctx = document.getElementById('centrosChart') as HTMLCanvasElement;
    if (!ctx) return;
    
    if (this.charts.centrosUtilizados) {
      this.charts.centrosUtilizados.destroy();
    }

    const data = this.centrosUtilizados || [];
    const labels = data.map((d: any) => d.centro);
    const values = data.map((d: any) => d.total_citas);

    this.charts.centrosUtilizados = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels.length ? labels : ['Sin datos'],
        datasets: [{
          label: 'Total Citas',
          data: values.length ? values : [0],
          backgroundColor: [
            'rgba(3, 105, 161, 0.8)',
            'rgba(14, 165, 233, 0.8)',
            'rgba(6, 182, 212, 0.8)',
            'rgba(20, 184, 166, 0.8)',
            'rgba(34, 197, 94, 0.8)'
          ],
          borderRadius: 8,
          borderSkipped: false
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { 
            beginAtZero: true, 
            ticks: { color: '#64748B', font: { size: 12 } },
            grid: { color: 'rgba(0,0,0,0.05)' }
          },
          y: { 
            ticks: { color: '#1E293B', font: { size: 13, weight: 500 } },
            grid: { display: false }
          }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  }

  createFacturasChart(): void {
    const ctx = document.getElementById('facturasChart') as HTMLCanvasElement;
    if (!ctx) return;
    
    if (this.charts.facturas) {
      this.charts.facturas.destroy();
    }

    const estado = this.estadisticas.facturas_por_estado || {};

    this.charts.facturas = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Pagadas', 'Pendientes'],
        datasets: [{
          data: [estado.pagada || 0, estado.pendiente || 0],
          backgroundColor: ['#22c55e', '#f59e0b'],
          borderWidth: 3,
          borderColor: '#fff',
          hoverOffset: 10
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '65%',
        plugins: {
          legend: { 
            position: 'bottom', 
            labels: { 
              color: '#1E293B',
              padding: 15,
              font: { size: 12, weight: 500 },
              usePointStyle: true,
              pointStyle: 'circle'
            } 
          }
        }
      }
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

    if (!a.tipo_documento) {
      this.notification.error('El tipo de documento es requerido');
      return;
    }

    if (!a.documento) {
      this.notification.error('El número de documento es requerido');
      return;
    }

    if (!a.id_plan) {
      this.notification.error('El plan de salud es requerido');
      return;
    }

    // Validar cantidad de dígitos según tipo de documento
    const docLength = a.documento.length;
    let minLen = 6, maxLen = 10;

    if (a.tipo_documento === 'RC') {
      minLen = 6; maxLen = 10;
    } else if (a.tipo_documento === 'TI') {
      minLen = 7; maxLen = 10;
    } else if (a.tipo_documento === 'CC') {
      minLen = 6; maxLen = 10;
    }

    if (docLength < minLen || docLength > maxLen) {
      this.notification.error(`El documento debe tener entre ${minLen} y ${maxLen} dígitos para ${a.tipo_documento}`);
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

    // Validar edad según tipo de documento
    const hoy = new Date();
    const fechaNac = new Date(a.fecha_nacimiento);
    let edad = hoy.getFullYear() - fechaNac.getFullYear();
    const mesDiff = hoy.getMonth() - fechaNac.getMonth();
    if (mesDiff < 0 || (mesDiff === 0 && hoy.getDate() < fechaNac.getDate())) {
      edad--;
    }

    if (a.tipo_documento === 'RC') {
      if (edad > 6) {
        this.notification.error('El Registro Civil es solo para niños menores de 7 años');
        return;
      }
    } else if (a.tipo_documento === 'TI') {
      if (edad < 7 || edad > 17) {
        this.notification.error('La Tarjeta de Identidad es solo para niños de 7 a 17 años');
        return;
      }
    } else if (a.tipo_documento === 'CC') {
      if (edad < 18) {
        this.notification.error('La Cédula de Ciudadanía es solo para mayores de 18 años');
        return;
      }
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
        this.nuevoAfiliado = { email: '', password: '', nombre: '', tipo_documento: '', documento: '', telefono: '', direccion: '', fecha_nacimiento: '', id_plan: null };
        this.loadData();
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
    if (!this.nuevoProfesional.especialidad) {
      this.notification.error('La especialidad es requerida');
      return;
    }
    if (!this.nuevoProfesional.id_centro) {
      this.notification.error('El centro de salud es requerido');
      return;
    }
    this.loading = true;
    this.api.createProfesional(this.nuevoProfesional).subscribe({
      next: () => {
        this.notification.success('Profesional creado exitosamente');
        this.loading = false;
        this.nuevoProfesional = { email: '', password: '', nombre: '', especialidad: '', id_centro: null };
        this.loadData();
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
          this.loadData();
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
          this.loadData();
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
        this.loadData();
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
        this.loadData();
      },
      error: (err: any) => this.notification.error(err.error?.error || 'Error')
    });
  }

  eliminarFactura(id: number): void {
    this.notification.confirmDanger('¿Está seguro de eliminar esta factura?', () => {
      this.api.deleteFactura(id).subscribe({
        next: () => {
          this.notification.success('Factura eliminada');
          this.loadData();
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
          this.loadData();
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
          this.loadData();
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
          this.loadData();
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
          this.loadData();
        },
        error: (err: any) => this.notification.error(err.error?.error || 'Error al eliminar')
      });
    });
  }

  cancelarEdicionCentro(): void {
    this.editandoCentro = false;
    this.nuevoCentro = { nombre: '', direccion: '', ciudad: '' };
  }

  // ── AFILIADOS: ver / editar / guardar / eliminar ──────────────────────────

  verAfiliado(a: any): void {
    this.afiliadoVer = a;
  }

  cerrarVerAfiliado(): void {
    this.afiliadoVer = null;
  }

  editarAfiliado(a: any): void {
    this.afiliadoVer = null;
    this.editandoAfiliado = true;
    this.afiliadoEditar = {
      id: a.id_afiliado,
      nombre: a.usuario?.nombre || '',
      telefono: a.telefono || '',
      direccion: a.direccion || '',
      id_plan: a.id_plan || null,
      fecha_nacimiento: a.fecha_nacimiento || ''
    };
  }

  guardarAfiliado(): void {
    const e = this.afiliadoEditar;
    if (!e.nombre?.trim()) {
      this.notification.error('El nombre es requerido');
      return;
    }
    if (e.telefono && !/^3\d{9}$/.test(e.telefono)) {
      this.notification.error('Teléfono inválido: 10 dígitos, empieza con 3');
      return;
    }
    if (e.fecha_nacimiento && e.fecha_nacimiento > this.maxFecha) {
      this.notification.error('La fecha de nacimiento no puede ser futura');
      return;
    }
    this.loading = true;
    this.api.updateAfiliado(e.id, {
      nombre: e.nombre,
      telefono: e.telefono,
      direccion: e.direccion,
      id_plan: e.id_plan,
      fecha_nacimiento: e.fecha_nacimiento
    }).subscribe({
      next: () => {
        this.notification.success('Afiliado actualizado');
        this.loading = false;
        this.editandoAfiliado = false;
        this.afiliadoEditar = {};
        this.loadData();
      },
      error: (err: any) => {
        this.notification.error(err.error?.error || 'Error al actualizar');
        this.loading = false;
      }
    });
  }

  cancelarEdicionAfiliado(): void {
    this.editandoAfiliado = false;
    this.afiliadoEditar = {};
  }

  eliminarAfiliado(id: number): void {
    this.notification.confirmDanger('¿Eliminar este afiliado? Se eliminará también su usuario.', () => {
      this.api.deleteAfiliado(id).subscribe({
        next: () => {
          this.notification.success('Afiliado eliminado');
          this.loadData();
        },
        error: (err: any) => this.notification.error(err.error?.error || 'Error al eliminar')
      });
    });
  }

  // ── PROFESIONALES: ver / editar / guardar / eliminar ─────────────────────

  verProfesional(p: any): void {
    this.profesionalVer = p;
  }

  cerrarVerProfesional(): void {
    this.profesionalVer = null;
  }

  editarProfesional(p: any): void {
    this.profesionalVer = null;
    this.editandoProfesional = true;
    this.profesionalEditar = {
      id: p.id_profesional,
      nombre: p.usuario?.nombre || '',
      especialidad: p.especialidad || '',
      id_centro: p.id_centro || null
    };
  }

  guardarProfesional(): void {
    const e = this.profesionalEditar;
    if (!e.nombre?.trim()) {
      this.notification.error('El nombre es requerido');
      return;
    }
    if (!e.especialidad?.trim()) {
      this.notification.error('La especialidad es requerida');
      return;
    }
    this.loading = true;
    this.api.updateProfesional(e.id, {
      nombre: e.nombre,
      especialidad: e.especialidad,
      id_centro: e.id_centro
    }).subscribe({
      next: () => {
        this.notification.success('Profesional actualizado');
        this.loading = false;
        this.editandoProfesional = false;
        this.profesionalEditar = {};
        this.loadData();
      },
      error: (err: any) => {
        this.notification.error(err.error?.error || 'Error al actualizar');
        this.loading = false;
      }
    });
  }

  cancelarEdicionProfesional(): void {
    this.editandoProfesional = false;
    this.profesionalEditar = {};
  }

  eliminarProfesional(id: number): void {
    this.notification.confirmDanger('¿Eliminar este profesional? Se eliminará también su usuario.', () => {
      this.api.deleteProfesional(id).subscribe({
        next: () => {
          this.notification.success('Profesional eliminado');
          this.loadData();
        },
        error: (err: any) => this.notification.error(err.error?.error || 'Error al eliminar')
      });
    });
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}