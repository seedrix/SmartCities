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

  ngOnInit(): void {
    let shopList = this.shops.getShopList()
    console.log(shopList)
  }

  ngAfterContentInit() {
    this.navbar.showNavbar()
  }

  sendShopList() {
    console.log(this.selectedShops)
    let selectedIDs = []
    this.selectedShops.forEach((shop: Shop) => {
      selectedIDs.push(shop.shop_id)
    });
    this.shops.setSelection(selectedIDs)
  }

}
