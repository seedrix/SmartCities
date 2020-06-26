import { Component } from '@angular/core';
import { ShopsService } from './services/shops.service';
import {
  trigger,
  state,
  style,
  animate,
  transition,
} from '@angular/animations';
import { NavbarService } from './services/navbar.service';
import { AuthService } from './services/auth.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
  animations: [
    trigger('showHideDisplays', [
      // ...
      state('open', style({
        height: '*',
        overflow: 'hidden',
        opacity: 1,
      })),
      state('closed', style({
        height: '0px',
        overflow: 'hidden',
      })),
      transition('open => closed', [
        animate('0.8s')
      ]),
      transition('closed => open', [
        animate('0.4s')
      ]),
    ]),
  ],
})
export class AppComponent {
  title = 'frontend';
  showDisplays = false
  constructor(public shops: ShopsService, public navbar: NavbarService, private authService: AuthService) {
  }

  toggleDisplays() {
    this.showDisplays = !this.showDisplays
  }

  hideNavbar() {
    this.navbar.hideNavbar()
  }

  showNavbar() {
    this.navbar.showNavbar();
  }

  hideNavbarCalled() {
    console.log("hide")
  }

  logout() {
    this.authService.logout("login");
  }
}
