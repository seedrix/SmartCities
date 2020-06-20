import { Injectable } from '@angular/core';
import {Shop} from '../utility/shop';

@Injectable({
  providedIn: 'root'
})
export class ShopsService {
  public shop_list: {[name: string]: Shop} = {
    "Adidas": new Shop("Adidas", 5, 5),
    "Netto": new Shop("Netto", 10, 5),
    "Modepark": new Shop("Modepark", 5, 10),
    "H&M": new Shop("H&M", 8, 10),
    "Drogerie": new Shop("Drogerie", 10, 8)
  }
  

  constructor() { }
}
