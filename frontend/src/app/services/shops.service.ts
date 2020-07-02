import { Injectable } from '@angular/core';
import { Shop } from '../utility/shop';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, retry } from 'rxjs/operators';
import { MatSnackBar } from '@angular/material/snack-bar';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class ShopsService {
  url = "https://t1.max-reichel.de:4433/"
  shopsAllUrl = this.url + "shops/all"
  getShopListUrl = this.url + "user/shops"
  postShopsUrl = this.url + "user/shops"
  nextShopUrl = this.url + "user/next_shop"


  shopsSelected = false
  selection: Shop[];
  nextShop: Shop;

  public shop_list: { [name: string]: Shop } = {};


  constructor(private http: HttpClient, private snackbar: MatSnackBar, private authService: AuthService) {
    this.http.get(this.shopsAllUrl).subscribe((values: [any]) => {
      values.forEach(shop => {
        this.shop_list[shop.shop_name] = new Shop(shop.shop_name, shop.shop_id, shop.max_people)
        console.log(shop)
      });
    }, error => {
      console.log(error)
    });



  }

  async setSelection(shops: Shop[]) {
    const httpOptions = this.createHttpPostOptions();
    const json = this.createJSON(shops)
    try {
      const response = await this.http.post(this.postShopsUrl, json, httpOptions).toPromise();
      this.shopsSelected = true
      this.selection = shops
      this.snackbar.open("Shop list saved.", "", {
        duration: 4000,
      });
      console.log(response)
    } catch (error) {
      console.log("Error Status: " + error.status)
      console.log(error)
      this.snackbar.open("Could not reach the backend server.", "", {
        duration: 2000,
      });
    }

  }

  async getShopList() {
    const httpOptions = this.createHttpGetOptions();
    try {
      const response = await this.http.get(this.getShopListUrl, httpOptions).toPromise();
      console.log(response)
    } catch (error) {
      console.log("Error Status: " + error.status)
      console.log(error)
      this.snackbar.open("Could not reach the backend server.", "", {
        duration: 2000,
      });
    }
  }

  createJSON(shops) {
    const json = shops
    return json
  }

  createHttpGetOptions() {
    const token = this.authService.token;
    return {
      headers: new HttpHeaders({
        'Authorization': "Bearer " + token,
      })
    }
  }

  createHttpPostOptions() {
    const token = this.authService.token;
    return {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Authorization': "Bearer " + token,
      })
    }
  }

  async getNextShop() {
    try {
      const response = await this.http.get(this.nextShopUrl).toPromise();

      console.log(response)
    } catch (error) {
      console.log("Error Status: " + error.status)
      this.snackbar.open("Could not reach the backend server.", "", {
        duration: 2000,
      });
    }
  }


  testShopList() {
    this.shop_list = {
      "Adidas": new Shop("Adidas", "1", 5),
      "Netto": new Shop("Netto", "2", 10),
      "Modepark": new Shop("Modepark", "3", 5),
      "H&M": new Shop("H&M", "4", 8),
      "Drogerie": new Shop("Drogerie", "5", 10)
    }
  }
}
