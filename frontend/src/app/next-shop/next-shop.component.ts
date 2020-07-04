import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import { ShopsService } from '../services/shops.service';
import { Shop } from '../utility/shop';
import { Router } from '@angular/router';


@Component({
  selector: 'app-next-shop',
  templateUrl: './next-shop.component.html',
  styleUrls: ['./next-shop.component.scss']
})
export class NextShopComponent implements OnInit {
  nextShop: Shop;
  logoSrc: string;
  allShopsVisited = false;

  constructor(public shops: ShopsService, private router: Router) { }

  async ngOnInit() {
    if (this.shops.shopsSelected) {
      let nextShop = await this.shops.getNextShop();
      this.nextShop = nextShop;
      this.logoSrc = nextShop.logo;
    }
  }

  async shopVisited() {
    await this.shops.shopVisited(this.nextShop)
    if (this.shops.shopsSelected) {
      this.allShopsVisited = true
    } else {
      let sameShop = true
      while (sameShop) {
        let nextShop = await this.shops.getNextShop();
        if (nextShop === undefined) {
          console.log(nextShop)
        }
        else if (nextShop.shop_id !== this.nextShop.shop_id) {
          let nextShop = await this.shops.getNextShop();
          this.nextShop = nextShop;
          this.logoSrc = nextShop.logo;
          sameShop = false;
        }
      }
    }
  }

  toShopList() {
    this.router.navigate(["/list"]);
  }

}


