import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class ShopsService {
  public shop_list = [{
    name: "Adidas",
    people: 7
  },
  {
    name: "Kaufland",
    people: 5
  },
  {
    name: "Nike",
    people: 5
  },
  {
    name: "Aldi",
    people: 1
  },
  {
    name: "Netto",
    people: 5
  }]

  constructor() { }
}
