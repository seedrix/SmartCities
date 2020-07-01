import { Component, OnInit } from '@angular/core';
import { ShopsService } from '../services/shops.service';
import { NavbarService } from '../services/navbar.service';

@Component({
  selector: 'app-list',
  templateUrl: './list.component.html',
  styleUrls: ['./list.component.scss']
})
export class ListComponent implements OnInit {  

  constructor(public shops: ShopsService, private navbar: NavbarService) { }

  ngOnInit(): void {
  }

  ngAfterContentInit() {
    this.navbar.showNavbar()
  }

  sendShopList() {
    this.shops.setSelection([])
  }

}
