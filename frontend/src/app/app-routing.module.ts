import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { ListComponent } from './list/list.component';
import { MonitorComponent } from './monitor/monitor.component';
import { DisplayComponent } from './display/display.component';
import { LoginComponent } from './login/login.component';
import { AuthGuardService } from './services/auth-guard.service';
import { HistoryComponent } from './history/history.component';


const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent  },
  { path: 'list', component: ListComponent, canActivate: [ AuthGuardService ]  },
  { path: 'history', component: HistoryComponent, canActivate: [ AuthGuardService ]  },
  { path: 'monitor', component: MonitorComponent, canActivate: [ AuthGuardService ]  },
  { path: 'display/:id', component: DisplayComponent, canActivate: [ AuthGuardService ] },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
