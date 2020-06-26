import { Injectable } from '@angular/core';
import { Router, CanActivate, RouterStateSnapshot, ActivatedRouteSnapshot } from '@angular/router';
import { AuthService } from './auth.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Injectable({
  providedIn: 'root'
})
export class AuthGuardService implements CanActivate {

  constructor(public authService: AuthService, public router: Router, private snackbar: MatSnackBar) {}

  async canActivate(route: ActivatedRouteSnapshot) {
    if (!await this.authService.checkAuthenticated()) {
      let desiredUrl = route.routeConfig.path
      this.authService.setRedirectUrl(desiredUrl)
      await this.router.navigate(['login']);
      this.snackbar.open("You need to be logged in to use this functionality. Please login.", "", {
        duration: 4000,
      });
      return false;
    }
    return true;
  }
}