from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any

from .core import TraderNetCore


class Trading(TraderNetCore):
    def open_security_session(
        self,
        *args: bool,
        **kwargs: bool
    ) -> Callable[[str], dict[str, Any]]:
        """
        Opening a new security session.

        Returns
        -------
        result : Callable[[str], dict]
            A function that accepts a security code and returns an answer
            containing login information.

        Notes
        -----
        Use it as follows:
        >>> trade = Trading.from_config('tradernet.ini')
        >>> opening = trade.open_security_session(False, True)  # Send to app
        >>> opening(123456)  # Push you received
        """
        self.send_security_sms(*args, **kwargs)
        return lambda token: self.open_with_sms(str(token))

    def buy(
        self,
        symbol: str,
        quantity: int = 1,
        price: float = 0.0,
        duration: str = 'day',
        use_margin: bool = True,
        custom_order_id: int | None = None
    ) -> dict[str, Any]:
        """
        Placing a new buy order.

        Parameters
        ----------
        symbol : str
            Tradernet symbol.
        quantity : int, optional
            Units of the symbol, by default 1.
        price : float, optional
            Limit price, by default 0.0 that means market order.
        duration : str, optional
            Time to order expiration, by default 'day'.
        use_margin : bool, optional
            If margin credit might be used, by default True.
        custom_order_id : int, optional
            Custom order ID, by default None meaning that it will be generated
            by Tradernet.

        Returns
        -------
        dict[str, Any]
            Order information.
        """
        if quantity <= 0:
            raise ValueError('Quantity must be positive')

        return self.trade(
            symbol,
            quantity,
            price,
            duration,
            use_margin,
            custom_order_id
        )

    def sell(
        self,
        symbol: str,
        quantity: int = 1,
        price: float = 0.0,
        duration: str = 'day',
        use_margin: bool = True,
        custom_order_id: int | None = None
    ) -> dict[str, Any]:
        """
        Placing a new sell order.

        Parameters
        ----------
        symbol : str
            Tradernet symbol.
        quantity : int, optional
            Units of the symbol, by default 1.
        price : float, optional
            Limit price, by default 0.0 that means market order.
        duration : str, optional
            Time to order expiration, by default 'day'.
        use_margin : bool, optional
            If margin credit might be used, by default True.
        """
        if quantity <= 0:
            raise ValueError('Quantity must be positive')

        return self.trade(
            symbol,
            -quantity,
            price,
            duration,
            use_margin,
            custom_order_id
        )

    def stop(self, symbol: str, price: float) -> dict[str, Any]:
        """
        Placing a new stop order on a certain open position.

        Parameters
        ----------
        symbol : str
            Tradernet symbol.
        price : float
            Stop price.

        Returns
        -------
        dict[str, Any]
            Order information.
        """
        return self.authorized_request(
            'putStopLoss',
            {'instr_name': symbol, 'stop_loss': price}
        )

    def trailing_stop(self, symbol: str, percent: int = 1) -> dict[str, Any]:
        """
        Placing a new trailing stop order on a certain open position.

        Parameters
        ----------
        symbol : str
            Tradernet symbol.
        percent : int, optional
            Stop loss percentage, by default 1.

        Returns
        -------
        dict[str, Any]
            Order information.
        """
        return self.authorized_request(
            'putStopLoss',
            {
                'instr_name': symbol,
                'stop_loss_percent': percent,
                'stoploss_trailing_percent': percent
            }
        )

    def take_profit(self, symbol: str, price: float) -> dict[str, Any]:
        """
        Placing a new take profit order on a certain open position.

        Parameters
        ----------
        symbol : str
            Tradernet symbol.
        price : float
            Take profit price.

        Returns
        -------
        dict[str, Any]
            Order information.
        """
        return self.authorized_request(
            'putStopLoss',
            {'instr_name': symbol, 'take_profit': price}
        )

    def cancel(self, order_id: int) -> dict[str, Any]:
        """
        Cancelling an order.

        Parameters
        ----------
        order_id : int
            Order ID.
        """
        return self.authorized_request(
            'delTradeOrder',
            {'order_id': order_id}
        )

    def cancel_all(self) -> list[dict[str, Any]]:
        """
        Cancelling all orders.
        """
        active_orders = self.get_placed()['result']['orders']
        if 'order' not in active_orders:
            return []

        return [self.cancel(order['id']) for order in active_orders['order']]

    def get_placed(self, active: bool = True) -> dict[str, Any]:
        """
        Getting a list of orders in the current period.

        Parameters
        ----------
        active : bool, optional
            Show only active orders.

        Returns
        -------
        result : dict
            A dictionary of orders.

        Notes
        -----
        https://tradernet.ru/tradernet-api/orders-get-current-history
        """
        return self.authorized_request(
            'getNotifyOrderJson',
            {'active_only': int(active)}
        )

    def get_historical(
        self,
        start: datetime = datetime(2011, 1, 11),
        end: datetime = datetime.now()
    ) -> dict[str, Any]:
        """
        Getting a list of orders in the period.

        Parameters
        ----------
        start : datetime, optional
            Period start date.
        end : datetime, optional
            Period end date.

        Returns
        -------
        result : dict
            A dictionary of orders.

        Notes
        -----
        https://tradernet.ru/tradernet-api/get-orders-history
        """
        return self.authorized_request(
            'getOrdersHistory',
            {
                'from': start.strftime('%Y-%m-%dT%H:%M:%S'),
                'till': end.strftime('%Y-%m-%dT%H:%M:%S')
            }
        )

    def trade(
        self,
        symbol: str,
        quantity: int = 1,
        price: float = 0.0,
        duration: str = 'day',
        use_margin: bool = True,
        custom_order_id: int | None = None
    ) -> dict[str, Any]:
        """
        Placing a new buy order.

        Parameters
        ----------
        symbol : str
            A Tradernet symbol.
        quantity : int, optional
            Units of the symbol, by default 1. If negative, then it is a sale.
        price : float, optional
            Limit price, by default 0.0 that means market order.
        duration : str, optional
            Time to order expiration, by default 'day'.
        use_margin : bool, optional
            If margin credit might be used, True by default.
        custom_order_id : int, optional
            Custom order ID, by default None meaning that it will be generated
            by Tradernet.

        Returns
        -------
        dict[str, Any]
            Order information.
        """
        # IOC emulation is much slower than the real IOC, because emulation
        # requires two sent and two received FIX messages instead of only one
        # pair, so total execution time is about 0.5 sec.
        if duration == 'ioc':
            order = self.trade(
                symbol,
                quantity,
                price,
                'day',
                use_margin,
                custom_order_id
            )
            if 'order_id' in order:
                self.cancel(order['order_id'])
            return order

        duration = duration.lower()
        if duration not in self.DURATION:
            raise ValueError(f'Unknown duration {duration}')

        if quantity > 0:    # buy
            action_id = 2 if use_margin else 1
        elif quantity < 0:  # sale
            action_id = 4 if use_margin else 3
        else:
            raise ValueError('Zero quantity!')

        return self.authorized_request(
            'putTradeOrder',
            {
                'instr_name': symbol,
                'action_id': action_id,
                'order_type_id': 2 if price else 1,
                'qty': abs(quantity),
                'limit_price': price,
                'expiration_id': self.DURATION[duration],
                'user_order_id': custom_order_id
            }
        )
