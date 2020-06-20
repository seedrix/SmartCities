import { Injectable, EventEmitter, Output } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class NavbarService {
  visible = true;
  @Output() show = new EventEmitter<any>();
  @Output() hide = new EventEmitter<any>();

  toggle() {
    this.visible = !this.visible;
    if (this.visible) {
      this.show.emit(null);
    } else {
      this.hide.emit(null);
    }
  }

  showNavbar() {
    this.visible = true
    this.show.emit(null);
  }

  hideNavbar() {
    this.visible = false
    this.hide.emit(null);
  }


}
