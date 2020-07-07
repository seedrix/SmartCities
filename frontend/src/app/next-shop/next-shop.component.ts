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
  waitForNextShop = false;

  constructor(public shops: ShopsService, private router: Router) { }

  async ngOnInit() {
    if (Object.keys(this.shops.userShops).length != 0) {
      this.getData()
    } else {
      this.shops.userShopsInit.subscribe(value => {
        if (value) {
          this.getData()
        }
      })
    }
  }

  async getData() {
    console.log("get data")
    console.log(this.shops.shopsSelected)
    console.log(this.shops.userShops)
    if (this.shops.shopsSelected) {
      console.log("shop is selected")
      let nextShop = await this.shops.getNextShop();
      this.nextShop = nextShop;
      this.logoSrc = nextShop.logo;

      // can happen if shops got unselected and the old planning value is retrieved
      if (!(this.nextShop.shop_id in this.shops.userShops)) {
        this.getNextShop()
      }
    }
  }

  async shopVisited() {
    await this.shops.shopVisited(this.nextShop)
    if (!this.shops.shopsSelected) {
      console.log("all shops visited")
      this.allShopsVisited = true
    } else {
      console.log("get next shop")
      this.getNextShop()
    }
  }

  async getNextShop() {
    this.waitForNextShop = true
    let sameShop = true
    console.log("query next shop")
    while (sameShop) {
      if (!this.shops.shopsSelected) {
        this.allShopsVisited = true
        break;
      }

      let nextShop = await this.shops.getNextShop();
      console.log(nextShop)
      
      if (nextShop === undefined) {
        console.log(nextShop)

      } else if (nextShop.shop_id !== this.nextShop.shop_id) {
        console.log("shop found")
        this.nextShop = nextShop;
        this.logoSrc = nextShop.logo;
        sameShop = false
      } else {
        console.log("same shop")
        sameShop = true
        await this.timeout(500)
      }
    }
    this.waitForNextShop = false
  }

  timeout(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  toShopList() {
    this.router.navigate(["/list"]);
  }

}


