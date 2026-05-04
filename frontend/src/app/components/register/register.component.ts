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
  rol = '';
  email = '';
  password = '';
  confirmPassword = '';
  nombre = '';
  apellido = '';
  telefono = '';
  fecha_nacimiento = '';
  especialidad = '';
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
    
    const data: any = {
      rol: this.rol,
      email: this.email,
      password: this.password,
      nombre: this.nombre,
      apellido: this.apellido,
      telefono: this.telefono
    };
    
    if (this.rol === 'paciente' && this.fecha_nacimiento) {
      data.fecha_nacimiento = this.fecha_nacimiento;
    }
    
    if (this.rol === 'medico' && this.especialidad) {
      data.especialidad = this.especialidad;
    }

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