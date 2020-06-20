import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { ShopsService } from '../services/shops.service';
import { Shop } from '../utility/shop';

@Component({
  selector: 'app-display',
  templateUrl: './display.component.html',
  styleUrls: ['./display.component.scss']
})
export class DisplayComponent implements OnInit {
  id: string;
  shop: Shop;

  constructor(private route: ActivatedRoute, private shops: ShopsService) { }

  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {
      this.id = params.get('id');
      this.shop = this.shops.shop_list[this.id]
      console.log(this.id)
    })


  }

}
