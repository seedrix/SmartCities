import { Component, OnInit } from '@angular/core';
import { ShopsService } from '../services/shops.service';

@Component({
  selector: 'app-next-shop',
  templateUrl: './next-shop.component.html',
  styleUrls: ['./next-shop.component.scss']
})
export class NextShopComponent implements OnInit {

  constructor(public shops: ShopsService) { }

  ngOnInit(): void {
  }

  shopVisited() {
    
  }

}
