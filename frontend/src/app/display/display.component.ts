import { Component, OnInit, AfterViewInit, ChangeDetectorRef } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { ShopsService } from '../services/shops.service';
import { Shop } from '../utility/shop';
import { NavbarService } from '../services/navbar.service';

@Component({
  selector: 'app-display',
  templateUrl: './display.component.html',
  styleUrls: ['./display.component.scss']
})
export class DisplayComponent implements OnInit {
  id: string;
  shop: Shop;

  constructor(private route: ActivatedRoute, private shops: ShopsService, private navbar: NavbarService, private changeDetector : ChangeDetectorRef) { }

  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {
      this.id = params.get('id');
      this.shop = this.shops.shop_list[this.id]
    })
  }

  ngAfterContentInit() {
    this.navbar.hideNavbar()
  }

}
