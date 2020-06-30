import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {
  public form: FormGroup;
  public registerForm: FormGroup;
  public loginInvalid: boolean;
  private formSubmitAttempt: boolean;
  private returnUrl: string;
  public login: boolean = true;

  constructor(
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    private authService: AuthService,
    private snackBar: MatSnackBar
  ) {
  }

  async ngOnInit() {
    this.returnUrl = this.route.snapshot.queryParams.returnUrl || '/list';

    this.form = this.fb.group({
      username: ['', Validators.email],
      password: ['', Validators.required]
    });

    this.registerForm = this.fb.group({
      username: ['', Validators.email],
      password: ['', Validators.required]
    });

    if (await this.authService.checkAuthenticated()) {
      await this.router.navigate([this.returnUrl]);
    }
  }

  async onSubmit() {
    this.loginInvalid = false;
    this.formSubmitAttempt = false;
    if (this.form.valid) {
      try {
        const username = this.form.get('username').value;
        const password = this.form.get('password').value;
        await this.authService.login(username, password);
      } catch (err) {
        this.loginInvalid = true;
      }
    } else {
      this.formSubmitAttempt = true;
    }
  }

  openRegisterForm() {
    this.login = false;
  }

  openLoginForm() {
    this.login = true;
  }

  doLoginEnter(event: KeyboardEvent) {
    if ((event.key === "Enter") && this.form.valid) {
      this.doLogin()
    }
  }
  doRegisterEnter(event: KeyboardEvent) {
    if ((event.key === "Enter") && this.registerForm.valid) {
      this.doRegister()
    }
  }

  doRegister() {
  }

  doLogin() {
  }

  loggedIn() {
    this.router.navigate([this.authService.redirectUrl]);

  }
}