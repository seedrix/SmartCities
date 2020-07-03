export class Shop {
    name: string;
    people: number;
    maxPeople: number;
    shop_id: string;
    isStop: boolean;
    waitingTime: number;
    logo: string;

    

    constructor(name: string, shop_id: string, maxPeople: number, logo: string) {
        this.name = name;
        this.maxPeople = maxPeople;
        this.shop_id = shop_id;
        this.logo = logo;
    }
}