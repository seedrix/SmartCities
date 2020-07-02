import { Component, OnInit } from '@angular/core';
import { ShopsService } from '../services/shops.service';
import { NavbarService } from '../services/navbar.service';
import { Shop } from '../utility/shop';

@Component({
  selector: 'app-list',
  templateUrl: './list.component.html',
  styleUrls: ['./list.component.scss']
})
export class ListComponent implements OnInit {  
  selectedShops: any = [];

  constructor(public shops: ShopsService, private navbar: NavbarService) { }

  async ngOnInit() {
    let shopList = await this.shops.getShopList()
    if (shopList) {
      console.log(shopList)
      this.selectedShops = shopList
    }
  }

  ngAfterContentInit() {
    this.navbar.showNavbar()
  }

  sendShopList() {
    this.shops.setSelection(this.selectedShops)
  }

}
