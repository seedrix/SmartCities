import { Injectable } from '@angular/core';
import { Shop } from '../utility/shop';
import { HttpClient } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, retry } from 'rxjs/operators';
import { MatSnackBar } from '@angular/material/snack-bar';

@Injectable({
  providedIn: 'root'
})
export class ShopsService {
  url = "https://t1.max-reichel.de:4433/shops/all"
  shopsSelected = false
  selection: Shop[];
  nextShop: Shop;

  public shop_list: { [name: string]: Shop } = {};


  constructor(private http: HttpClient, private snackbar: MatSnackBar) {
    this.http.get(this.url).subscribe((values: [any]) => {
      values.forEach(shop => {
        this.shop_list[shop.shop_name] = new Shop(shop.shop_name, shop.max_people)
        console.log(shop)
      }, error => {
        console.log(error)
      });
    })

  }

  setSelection(shops: Shop[]) {

    this.shopsSelected = true
    this.selection = shops

  }

  testShopList() {
    this.shop_list = {
      "Adidas": new Shop("Adidas", 5),
      "Netto": new Shop("Netto", 10),
      "Modepark": new Shop("Modepark", 5),
      "H&M": new Shop("H&M", 8),
      "Drogerie": new Shop("Drogerie", 10)
    }
  }
}
