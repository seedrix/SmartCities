import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { ListComponent } from './list/list.component';
import { MonitorComponent } from './monitor/monitor.component';
import { LoginComponent } from './login/login.component';
import { AuthGuardService } from './services/auth-guard.service';
import { HistoryComponent } from './history/history.component';
import { NextShopComponent } from './next-shop/next-shop.component';
import { SensordataComponent } from './sensordata/sensordata.component';


const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent  },
  { path: 'list', component: ListComponent, canActivate: [ AuthGuardService ]  },
  { path: 'next', component: NextShopComponent, canActivate: [ AuthGuardService ]  },
  { path: 'history', component: HistoryComponent, canActivate: [ AuthGuardService ]  },
  { path: 'current', component: MonitorComponent, canActivate: [ AuthGuardService ]  },
  { path: 'sensordata', component: SensordataComponent, canActivate: [ AuthGuardService ]  },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
