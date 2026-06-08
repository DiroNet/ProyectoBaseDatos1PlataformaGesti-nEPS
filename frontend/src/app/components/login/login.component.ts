import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { NotificationService } from '../../services/notification.service';

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

  constructor(
    private authService: AuthService,
    private router: Router,
    private notification: NotificationService
  ) {}

  onSubmit(): void {
    if (!this.email || !this.password) {
      this.notification.error('Ingrese email y contraseña');
      return;
    }

    this.loading = true;

    this.authService.login(this.email, this.password).subscribe({
      next: () => {
        this.notification.success('Bienvenido al sistema EPS Bienestar');
        setTimeout(() => {
          const role = this.authService.getUserRole();
          if (role === 'AFILIADO') this.router.navigate(['/dashboard-afiliado']);
          else if (role === 'PROFESIONAL') this.router.navigate(['/dashboard-profesional']);
          else if (role === 'ADMIN') this.router.navigate(['/dashboard-admin']);
          else this.router.navigate(['/error']);
        }, 1000);
      },
      error: (err: any) => {
        this.loading = false;
        this.notification.error(err.error?.error || 'Error al iniciar sesión');
      }
    });
  }
}