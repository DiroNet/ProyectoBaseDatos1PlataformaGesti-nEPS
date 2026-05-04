import { Routes } from '@angular/router';
import { LoginComponent } from './components/login/login.component';
import { RegisterComponent } from './components/register/register.component';
import { DashboardPacienteComponent } from './components/dashboard-paciente/dashboard-paciente.component';
import { DashboardMedicoComponent } from './components/dashboard-medico/dashboard-medico.component';
import { DashboardAdminComponent } from './components/dashboard-admin/dashboard-admin.component';

export const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'dashboard-paciente', component: DashboardPacienteComponent },
  { path: 'dashboard-medico', component: DashboardMedicoComponent },
  { path: 'dashboard-admin', component: DashboardAdminComponent },
  { path: '**', redirectTo: '/login' }
];