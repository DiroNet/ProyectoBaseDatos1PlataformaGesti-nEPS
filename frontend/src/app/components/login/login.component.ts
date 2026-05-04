import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})
export class LoginComponent {
  email = '';
  password = '';
  loading = false;
  error = '';
  showNotification = false;
  notificationType = '';
  notificationMessage = '';

  showNotify(message: string, type: string, duration = 3000): void {
    this.notificationMessage = message;
    this.notificationType = type;
    this.showNotification = true;
    setTimeout(() => this.showNotification = false, duration);
  }

  constructor(private authService: AuthService, private router: Router) {}

  onSubmit(): void {
    this.loading = true;
    this.error = '';
    
    this.authService.login(this.email, this.password).subscribe({
      next: () => {
        const role = this.authService.getUserRole();
        if (role === 'paciente') this.router.navigate(['/dashboard-paciente']);
        else if (role === 'medico') this.router.navigate(['/dashboard-medico']);
        else if (role === 'administrador') this.router.navigate(['/dashboard-admin']);
        else this.router.navigate(['/']);
      },
      error: (err: any) => {
        this.error = err.error?.error || 'Error al iniciar sesión';
        this.loading = false;
        this.showNotify(this.error, 'error');
      }
    });
  }
}