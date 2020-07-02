import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import { ShopsService } from '../services/shops.service';
import { Shop } from '../utility/shop';

@Component({
  selector: 'app-next-shop',
  templateUrl: './next-shop.component.html',
  styleUrls: ['./next-shop.component.scss']
})
export class NextShopComponent implements OnInit {
  nextShop: Shop;

  constructor(public shops: ShopsService) { }

  async ngOnInit() {
    if (this.shops.shopsSelected) {
      let nextShop = await this.shops.getNextShop();
      this.nextShop = nextShop;
    }
  }

  shopVisited() {

  }

}
