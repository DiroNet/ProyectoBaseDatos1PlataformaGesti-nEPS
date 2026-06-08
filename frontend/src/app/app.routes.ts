import { Routes } from '@angular/router';
import { LoginComponent } from './components/login/login.component';
import { RegisterComponent } from './components/register/register.component';
import { DashboardAfiliadoComponent } from './components/dashboard-afiliado/dashboard-afiliado.component';
import { DashboardProfesionalComponent } from './components/dashboard-profesional/dashboard-profesional.component';
import { DashboardAdminComponent } from './components/dashboard-admin/dashboard-admin.component';
import { ErrorPageComponent } from './components/error-page/error-page.component';

export const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'dashboard-afiliado', component: DashboardAfiliadoComponent },
  { path: 'dashboard-profesional', component: DashboardProfesionalComponent },
  { path: 'dashboard-admin', component: DashboardAdminComponent },
  { path: 'error', component: ErrorPageComponent },
  { path: '**', component: ErrorPageComponent }
];
