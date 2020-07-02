export class Shop {
    name: string;
    people: number;
    maxPeople: number;
    shop_id: string;
    isStop: boolean;
    waitingTime: number;

    

    constructor(name: string, shop_id: string, maxPeople: number) {
        this.name = name;
        this.maxPeople = maxPeople;
        this.shop_id = shop_id;

        // if (this.people >= this.maxPeople) {
        //     this.isStop = true
        // } else {
        //     this.isStop = false
        // }
    }
}