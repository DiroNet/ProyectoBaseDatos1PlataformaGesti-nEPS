import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { ApiService } from '../../services/api.service';
import { NotificationService } from '../../services/notification.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './register.component.html',
  styleUrl: './register.component.css'
})
export class RegisterComponent {
  email = '';
  password = '';
  confirmPassword = '';
  nombre = '';
  documento = '';
  tipoDocumento = '';
  telefono = '';
  direccion = '';
  fechaNacimiento = '';
  id_plan: number | null = null;
  planes: any[] = [];
  loading = false;
  maxFecha = new Date().toISOString().split('T')[0];
  
  maxFechaNacimiento = '';
  minFechaNacimiento = '';
  mensajeFechaNacimiento = '';

  constructor(
    private authService: AuthService,
    private router: Router,
    private api: ApiService,
    private notification: NotificationService
  ) {
    this.loadPlanes();
  }

  loadPlanes(): void {
    this.api.getPlanes().subscribe({
      next: (data: any) => this.planes = data,
      error: (err: any) => console.error(err)
    });
  }

  actualizarLimitesFechaNacimiento(): void {
    const hoy = new Date();
    
    if (this.tipoDocumento === 'RC') {
      // RC: 0 a 6 años - máximo hace 6 años, mínimo hoy
      const maxDate = new Date(hoy);
      maxDate.setFullYear(hoy.getFullYear() - 6);
      this.maxFechaNacimiento = maxDate.toISOString().split('T')[0];
      this.minFechaNacimiento = '';
      this.mensajeFechaNacimiento = 'Para Registro Civil, la fecha debe ser máximo hace 6 años (menores de 7 años)';
    } else if (this.tipoDocumento === 'TI') {
      // TI: 7 a 17 años - máximo hace 7 años, mínimo hace 17 años
      const maxDate = new Date(hoy);
      maxDate.setFullYear(hoy.getFullYear() - 7);
      const minDate = new Date(hoy);
      minDate.setFullYear(hoy.getFullYear() - 17);
      this.maxFechaNacimiento = maxDate.toISOString().split('T')[0];
      this.minFechaNacimiento = minDate.toISOString().split('T')[0];
      this.mensajeFechaNacimiento = 'Para Tarjeta de Identidad, la edad debe ser entre 7 y 17 años';
    } else if (this.tipoDocumento === 'CC') {
      // CC: 18+ años - máximo hace 18 años, mínimo hace 100 años
      const maxDate = new Date(hoy);
      maxDate.setFullYear(hoy.getFullYear() - 18);
      const minDate = new Date(hoy);
      minDate.setFullYear(hoy.getFullYear() - 100);
      this.maxFechaNacimiento = maxDate.toISOString().split('T')[0];
      this.minFechaNacimiento = minDate.toISOString().split('T')[0];
      this.mensajeFechaNacimiento = 'Para Cédula de Ciudadanía, debe ser mayor de 18 años';
    } else {
      // Sin tipo seleccionado - solo no puede ser futura
      this.maxFechaNacimiento = this.maxFecha;
      this.minFechaNacimiento = '';
      this.mensajeFechaNacimiento = '';
    }
    
    // Limpiar fecha si está fuera de los nuevos límites
    if (this.fechaNacimiento) {
      const fechaSel = new Date(this.fechaNacimiento);
      const minD = this.minFechaNacimiento ? new Date(this.minFechaNacimiento) : null;
      const maxD = this.maxFechaNacimiento ? new Date(this.maxFechaNacimiento) : null;
      
      if ((maxD && fechaSel > maxD) || (minD && fechaSel < minD)) {
        this.fechaNacimiento = '';
      }
    }
  }

  onFechaNacimientoChange(): void {
    if (!this.fechaNacimiento || !this.tipoDocumento) return;
    
    const hoy = new Date();
    const fechaSel = new Date(this.fechaNacimiento);
    let edad = hoy.getFullYear() - fechaSel.getFullYear();
    const mesDiff = hoy.getMonth() - fechaSel.getMonth();
    if (mesDiff < 0 || (mesDiff === 0 && hoy.getDate() < fechaSel.getDate())) {
      edad--;
    }
    
    if (this.tipoDocumento === 'RC' && edad > 6) {
      this.notification.warning('La fecha no es válida para Registro Civil (menores de 7 años)');
      this.fechaNacimiento = '';
    } else if (this.tipoDocumento === 'TI' && (edad < 7 || edad > 17)) {
      this.notification.warning('La fecha no es válida para Tarjeta de Identidad (7 a 17 años)');
      this.fechaNacimiento = '';
    } else if (this.tipoDocumento === 'CC' && edad < 18) {
      this.notification.warning('La fecha no es válida para Cédula (mayores de 18 años)');
      this.fechaNacimiento = '';
    }
  }

  filtrarTelefono(event: any): void {
    const input = event.target;
    let valor = input.value.replace(/\D/g, '');
    if (valor.length > 10) {
      valor = valor.substring(0, 10);
    }
    this.telefono = valor;
  }

  filtrarDocumento(event: any): void {
    const input = event.target;
    let valor = input.value.replace(/\D/g, '');
    
    // Límite según tipo de documento
    let maxLen = 10;
    if (this.tipoDocumento === 'RC' || this.tipoDocumento === 'TI') {
      maxLen = 10;
    } else if (this.tipoDocumento === 'CC') {
      maxLen = 10;
    }
    
    if (valor.length > maxLen) {
      valor = valor.substring(0, maxLen);
    }
    this.documento = valor;
  }

  preventNonNumeric(event: KeyboardEvent): void {
    const allowedKeys = ['Backspace', 'Delete', 'Tab', 'Escape', 'Enter', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'];
    if (allowedKeys.includes(event.key)) {
      return;
    }
    if (!/^\d$/.test(event.key)) {
      event.preventDefault();
    }
  }

  onSubmit(): void {
    if (!this.nombre.trim()) {
      this.notification.error('El nombre completo es requerido');
      return;
    }

    if (!this.email.trim()) {
      this.notification.error('El correo electrónico es requerido');
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(this.email)) {
      this.notification.error('Ingrese un correo electrónico válido');
      return;
    }

    if (!this.tipoDocumento) {
      this.notification.error('El tipo de documento es requerido');
      return;
    }

    if (!this.documento) {
      this.notification.error('El número de documento es requerido');
      return;
    }

    // Validar cantidad de dígitos según tipo de documento
    const docLength = this.documento.length;
    let minLen = 6, maxLen = 10;
    
    if (this.tipoDocumento === 'RC') {
      minLen = 6; maxLen = 10;
    } else if (this.tipoDocumento === 'TI') {
      minLen = 7; maxLen = 10;
    } else if (this.tipoDocumento === 'CC') {
      minLen = 6; maxLen = 10;
    }

    if (docLength < minLen || docLength > maxLen) {
      this.notification.error(`El documento debe tener entre ${minLen} y ${maxLen} dígitos para ${this.tipoDocumento}`);
      return;
    }

    if (!this.telefono) {
      this.notification.error('El teléfono celular es requerido');
      return;
    }
    if (!/^3\d{9}$/.test(this.telefono)) {
      this.notification.error('El teléfono debe ser un número móvil colombiano (10 dígitos, empieza con 3)');
      return;
    }

    if (!this.fechaNacimiento) {
      this.notification.error('La fecha de nacimiento es requerida');
      return;
    }
    if (this.fechaNacimiento > this.maxFecha) {
      this.notification.error('La fecha de nacimiento no puede ser una fecha futura');
      return;
    }

    // Validar edad según tipo de documento
    const hoy = new Date();
    const fechaNac = new Date(this.fechaNacimiento);
    let edad = hoy.getFullYear() - fechaNac.getFullYear();
    const mesDiff = hoy.getMonth() - fechaNac.getMonth();
    if (mesDiff < 0 || (mesDiff === 0 && hoy.getDate() < fechaNac.getDate())) {
      edad--;
    }

    if (this.tipoDocumento === 'RC') {
      // Registro Civil: 0 a 6 años
      if (edad > 6) {
        this.notification.error('El Registro Civil es solo para niños menores de 7 años');
        return;
      }
    } else if (this.tipoDocumento === 'TI') {
      // Tarjeta de Identidad: 7 a 17 años
      if (edad < 7 || edad > 17) {
        this.notification.error('La Tarjeta de Identidad es solo para niños de 7 a 17 años');
        return;
      }
    } else if (this.tipoDocumento === 'CC') {
      // Cédula: 18+ años
      if (edad < 18) {
        this.notification.error('La Cédula de Ciudadanía es solo para mayores de 18 años');
        return;
      }
    }

    if (!this.id_plan) {
      this.notification.error('El plan de salud es requerido');
      return;
    }

    if (!this.password) {
      this.notification.error('La contraseña es requerida');
      return;
    }
    if (this.password.length < 6) {
      this.notification.error('La contraseña debe tener al menos 6 caracteres');
      return;
    }

    if (this.password !== this.confirmPassword) {
      this.notification.error('Las contraseñas no coinciden');
      return;
    }

    this.loading = true;

    const data: any = {
      rol: 'AFILIADO',
      email: this.email,
      password: this.password,
      nombre: this.nombre,
      tipo_documento: this.tipoDocumento,
      documento: this.documento,
      telefono: this.telefono,
      direccion: this.direccion,
      fecha_nacimiento: this.fechaNacimiento,
      id_plan: this.id_plan
    };

    this.authService.register(data).subscribe({
      next: () => {
        this.notification.success('Registro exitoso. Ahora puede iniciar sesión.');
        this.loading = false;
        setTimeout(() => this.router.navigate(['/login']), 2000);
      },
      error: (err: any) => {
        this.loading = false;
        this.notification.error(err.error?.error || 'Error al registrar');
      }
    });
  }
}
