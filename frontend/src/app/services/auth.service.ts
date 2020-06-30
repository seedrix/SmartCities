import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
// import OktaAuth from '@okta/okta-auth-js';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  // private authClient = new OktaAuth({
  //   issuer: 'https://{YourOktaDomain}/oauth2/default',
  //   clientId: '{ClientId}'
  // });
  isLoggedIn = false
  redirectUrl: string = "/list";

  public isAuthenticated = new BehaviorSubject<boolean>(false);

  constructor(private router: Router, private snackbar: MatSnackBar) {
  }

  async checkAuthenticated() {
    // const authenticated = await this.authClient.session.exists();
    const authenticated = this.isLoggedIn

    this.isAuthenticated.next(authenticated);
    console.log(authenticated)
    return authenticated;
  }

  async login(username: string, password: string) {
    // const transaction = await this.authClient.signIn({username, password});

    // if (transaction.status !== 'SUCCESS') {
    //   throw Error('We cannot handle the ' + transaction.status + ' status');
    // }
    this.isLoggedIn = true
    this.isAuthenticated.next(true);
    this.snackbar.open("Logged in successfully.", "", {
      duration: 4000,
    });
    this.router.navigateByUrl("/" + this.redirectUrl)

    // this.authClient.session.setCookieAndRedirect(transaction.sessionToken);
  }

  async logout(redirect: string) {
    try {
      // await this.authClient.signOut();
      this.isLoggedIn = false
      this.isAuthenticated.next(false);
      this.router.navigate([redirect]);
    } catch (err) {
      console.error(err);
    }
  }

  setRedirectUrl(redirectUrl: string) {
    this.redirectUrl = redirectUrl
  }
}