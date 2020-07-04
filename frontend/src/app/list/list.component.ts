import { Component, OnInit } from '@angular/core';
import { ShopsService } from '../services/shops.service';
import { Shop } from '../utility/shop';

@Component({
  selector: 'app-list',
  templateUrl: './list.component.html',
  styleUrls: ['./list.component.scss']
})
export class ListComponent implements OnInit {  
  selectedShops: string[] = [];

  constructor(public shops: ShopsService) { }

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

  getData() {    
    let shopMap = this.shops.userShops
    let shopList = []
    if (shopMap) {
      for (let key in shopMap) {
        shopList.push(shopMap[key].shop_id)
      }
      this.selectedShops = shopList
    }

  }


  sendShopList() {
    this.shops.setSelection(this.selectedShops)
  }

}
