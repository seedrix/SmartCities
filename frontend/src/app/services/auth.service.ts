import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { ShopsService } from './shops.service';
// import OktaAuth from '@okta/okta-auth-js';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  url = "https://t1.max-reichel.de:4433/"
  signupUrl = this.url + "auth/signup"
  loginUrl = this.url + "auth/login"
  httpOptions = {
    headers: new HttpHeaders({
      'Content-Type': 'application/json',
    })
  };

  public isLoggedIn = false
  public isAdmin = false
  token: string
  redirectUrl: string = "/list";


  public isAuthenticated = new BehaviorSubject<boolean>(false);

  constructor(private router: Router, private snackbar: MatSnackBar, private http: HttpClient) {
  }

  async checkAuthenticated() {    
    let token = localStorage.getItem('token');
    if (token !== null) {
      this.fromToken(token)
    }
    const authenticated = this.isLoggedIn;
    return authenticated;
  }

  async register(username: string, password: string) {    
    const json = this.createJSON(username, password)
    try {
      const response = await this.http.post(this.signupUrl, json, this.httpOptions).toPromise();
      this.snackbar.open("Signed up successfully.", "", {
        duration: 4000,
      });
      this.loginSuccessful(response, username)
    } catch (error) {
      console.log("Error Status: " + error.status)
      if (error.status == 400) {
        this.snackbar.open("Account already exists.", "", {
          duration: 2000,
        });
      }
      else if (error.status == 401) {
        this.snackbar.open("No account with the given credentials found.", "", {
          duration: 2000,
        });

      } else {
        this.snackbar.open("Could not reach the backend server.", "", {
          duration: 2000,
        });
      }
    }

  }

  async login(username: string, password: string) {

    const json = this.createJSON(username, password)
    try {
      const response = await this.http.post(this.loginUrl, json, this.httpOptions).toPromise();
      this.snackbar.open("Logged in successfully.", "", {
        duration: 4000,
      });
      this.loginSuccessful(response, username)

    } catch (error) {
      console.log("Error Status: " + error.status)
      if (error.status == 400) {
        this.snackbar.open("Account already exists.", "", {
          duration: 2000,
        });
      } else if (error.status == 401) {
        this.snackbar.open("No account with the given credentials found.", "", {
          duration: 2000,
        });
      } else {
        this.snackbar.open("Could not reach the backend server.", "", {
          duration: 2000,
        });
      }
    }

  } 

  fromToken(token) {
    this.isLoggedIn = true;   
    let username = localStorage.getItem('username'); 
    this.token = token;
    if (username === "admin@admin.de") {
      this.isAdmin = true
    }

    this.isAuthenticated.next(true);
  }

  loginSuccessful(response, username) {
    this.isLoggedIn = true;    
    this.router.navigateByUrl("/" + this.redirectUrl)
    this.token = response.token;
    localStorage.setItem('token', this.token);
    localStorage.setItem('username', username);

    if (username === "admin@admin.de") {
      this.isAdmin = true
    }
    this.isAuthenticated.next(true);
  }

  createJSON(username: string, password: string) {
    const json = {
      "email": username,
      "password": password
    }
    return json;
  }

  async logout(redirect: string) {
    try {
      // await this.authClient.signOut();
      this.isLoggedIn = false
      this.isAdmin = false
      localStorage.removeItem('token');
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