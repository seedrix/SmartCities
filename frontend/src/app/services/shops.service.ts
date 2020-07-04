import { Injectable } from '@angular/core';
import { Shop } from '../utility/shop';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, throwError, BehaviorSubject } from 'rxjs';
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
  nextShop: Shop;

  public shopMap: { [shop_id: string]: Shop } = {};
  public userShops: { [shop_id: string]: Shop } = {};

  shopsInit: BehaviorSubject<boolean> = new BehaviorSubject(false);


  constructor(private http: HttpClient, private snackbar: MatSnackBar, private authService: AuthService) {
    this.getShops()

  }

  async getShops() {
    try {
      const response: any = await this.http.get(this.shopsAllUrl).toPromise();
      response.forEach(shop => {
        this.shopMap[shop.shop_id] = new Shop(shop.shop_name, shop.shop_id, shop.max_people, shop.logo);
        console.log(shop)
        
      });
      this.shopsInit.next(true);

    } catch (error) {
      console.log("Error Status: " + error.status)
      console.log(error)
      this.snackbar.open("Could not reach the backend server.", "", {
        duration: 2000,
      });
    }
  }

  async setSelection(shops: Shop[]) {
    const httpOptions = this.createHttpPostOptions();
    const json = this.createJSON(shops)
    try {
      const response = await this.http.post(this.postShopsUrl, json, httpOptions).toPromise();
      this.shopsSelected = true
      this.userShops = {}
      shops.forEach(shop => {
        this.userShops[shop.shop_id] = shop
      })
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
      const response: any = await this.http.get(this.getShopListUrl, httpOptions).toPromise();
      let shops = []
      response.forEach(shop_id => {
        shops.push(this.shopMap[shop_id])
      });

      this.userShops = {}
      shops.forEach(shop => {
        this.userShops[shop.shop_id] = shop
      })

      if (shops.length > 0) {
        this.shopsSelected = true
      }

      return response;


    } catch (error) {
      console.log("Error Status: " + error.status)
      console.log(error)
      this.snackbar.open("Could not reach the backend server.", "", {
        duration: 2000,
      });
    }
  }

  async shopVisited(shop: Shop) {
    const httpOptions = this.createHttpGetOptions();
    try {
      const response: any = await this.http.get(this.postShopsUrl + "/" + shop.shop_id, httpOptions).toPromise();
      delete this.userShops[shop.shop_id]

      if (Object.keys(this.userShops).length != 0) {
        this.shopsSelected = false
      }
      
      console.log(response)
      return response

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
    const httpOptions = this.createHttpGetOptions();
    try {
      const response: any = await this.http.get(this.nextShopUrl, httpOptions).toPromise();
      return this.shopMap[response];
    } catch (error) {
      console.log("Error Status: " + error.status)
      console.log(error)
      this.snackbar.open("Could not reach the backend server.", "", {
        duration: 2000,
      });
    }
  }


  // testShopList() {
  //   this.shop_list = {
  //     "Adidas": new Shop("Adidas", "1", 4),
  //     "Netto": new Shop("Netto", "2", 10),
  //     "Modepark": new Shop("Modepark", "3", 5),
  //     "H&M": new Shop("H&M", "4", 8),
  //     "Drogerie": new Shop("Drogerie", "5", 10)
  //   }
  // }
}
