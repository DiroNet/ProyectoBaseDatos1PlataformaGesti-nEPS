import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './register.component.html',
  styleUrl: './register.component.css'
})
export class RegisterComponent {
  rol = 'paciente';
  email = '';
  password = '';
  confirmPassword = '';
  nombre = '';
  apellido = '';
  telefono = '';
  cedula = '';
  fecha_nacimiento = '';
  direccion = '';
  especialidad = '';
  cedula_profesional = '';
  error = '';
  success = '';
  loading = false;
  showNotification = false;
  notificationType = '';
  notificationMessage = '';

  constructor(private authService: AuthService, private router: Router) {}

  showNotify(message: string, type: string, duration = 3000): void {
    this.notificationMessage = message;
    this.notificationType = type;
    this.showNotification = true;
    setTimeout(() => this.showNotification = false, duration);
  }

  onSubmit(): void {
    this.loading = true;
    this.error = '';
    this.success = '';
    
    if (this.password !== this.confirmPassword) {
      this.error = 'Las contraseñas no coinciden';
      this.loading = false;
      this.showNotify(this.error, 'error');
      return;
    }

    if (!this.cedula) {
      this.error = 'Por favor ingrese su cédula';
      this.loading = false;
      this.showNotify(this.error, 'error');
      return;
    }

    if (!this.fecha_nacimiento) {
      this.error = 'Por favor ingrese su fecha de nacimiento';
      this.loading = false;
      this.showNotify(this.error, 'error');
      return;
    }

    if (!this.telefono) {
      this.error = 'Por favor ingrese su teléfono';
      this.loading = false;
      this.showNotify(this.error, 'error');
      return;
    }

    const data: any = {
      rol: 'paciente',
      email: this.email,
      password: this.password,
      nombre: this.nombre,
      apellido: this.apellido,
      telefono: this.telefono,
      cedula: this.cedula,
      fecha_nacimiento: this.fecha_nacimiento,
      direccion: this.direccion
    };

    this.authService.register(data).subscribe({
      next: () => {
        this.success = 'Registro exitoso. Por favor inicie sesión.';
        this.loading = false;
        this.showNotify(this.success, 'success');
        setTimeout(() => this.router.navigate(['/login']), 2000);
      },
      error: (err: any) => {
        this.error = err.error?.error || 'Error al registrar';
        this.loading = false;
        this.showNotify(this.error, 'error');
      }
    });
  }
}