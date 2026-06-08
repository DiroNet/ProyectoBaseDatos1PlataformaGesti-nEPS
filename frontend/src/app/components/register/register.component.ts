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
  telefono = '';
  direccion = '';
  fechaNacimiento = '';
  id_plan: number | null = null;
  planes: any[] = [];
  loading = false;

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

  filtrarNumeros(event: any, campo: string): void {
    const input = event.target;
    const valor = input.value.replace(/\D/g, '');
    if (campo === 'documento') {
      this.documento = valor;
    } else if (campo === 'telefono') {
      this.telefono = valor;
    }
  }

  onSubmit(): void {
    if (!this.email || !this.password || !this.nombre) {
      this.notification.error('Complete los campos requeridos');
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(this.email)) {
      this.notification.error('Ingrese un email válido');
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

    if (!this.documento || this.documento.length < 6 || this.documento.length > 10) {
      this.notification.error('La cédula debe tener entre 6 y 10 dígitos');
      return;
    }

    if (!/^3\d{9}$/.test(this.telefono)) {
      this.notification.error('El teléfono debe ser un número móvil colombiano (10 dígitos, empieza con 3)');
      return;
    }

    this.loading = true;

    const data: any = {
      rol: 'AFILIADO',
      email: this.email,
      password: this.password,
      nombre: this.nombre,
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
