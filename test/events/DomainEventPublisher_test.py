from datetime import datetime
from typing import Any, List, Type

from returns.future import FutureResult, FutureSuccess

from dino_seedwork_be.domain.DomainEventPublisher import DomainEventPublisher
from dino_seedwork_be.domain.DomainEventSubscriber import DomainEventSubscriber
from dino_seedwork_be.utils.functional import return_v, throw_exception

from .TestableDomainEvent import (AnotherTestableDomainEvent,
                                  TestableDomainEvent)

event_type = "test_event"
test_event = TestableDomainEvent(name=event_type, occurred_on=datetime.now())


class TestDomainEventPublisher:
    event_handled = False
    another_event_handled = False

    class TestDomainEventSubscriber(DomainEventSubscriber):
        def handle_event(
            self, an_event: TestableDomainEvent
        ) -> FutureResult[Any, Exception]:
            assert an_event.name() == test_event.name()
            TestDomainEventPublisher.event_handled = True
            return FutureSuccess(None)

        def event_type_subscribed(self) -> List[str] | str:
            return event_type

    async def test_domain_event_publisher_publish(self):
        DomainEventPublisher.instance().reset()
        DomainEventPublisher.instance().subscribe(self.TestDomainEventSubscriber())
        assert DomainEventPublisher.instance().is_lock() == False
        assert DomainEventPublisher.instance().has_subscribers() == True
        assert TestDomainEventPublisher.event_handled == False

        await DomainEventPublisher.instance().publish(test_event).lash(
            throw_exception
        ).awaitable()

        assert TestDomainEventPublisher.event_handled == True

    async def test_domain_event_publisher_blocked(self):
        another_test_event_type = "TestDomainEvent"
        another_test_event = AnotherTestableDomainEvent(another_test_event_type)
        TestDomainEventPublisher.event_handled = False
        TestDomainEventPublisher.another_event_handled = False

        class TestDomainEventSubscriber(DomainEventSubscriber):
            def handle_event(
                self, an_event: TestableDomainEvent
            ) -> FutureResult[Any, Exception]:
                assert an_event.name() == test_event.name()
                TestDomainEventPublisher.event_handled = True
                return (
                    DomainEventPublisher.instance()
                    .publish(another_test_event)
                    .map(return_v("OK"))
                )

            def event_type_subscribed(self) -> str:
                return event_type

        class AnotherTestDomainEventSubscriber(DomainEventSubscriber):
            def handle_event(
                self, an_event: AnotherTestableDomainEvent
            ) -> FutureResult[Any, Exception]:
                TestDomainEventPublisher.another_event_handled = True
                return FutureSuccess(None)

            def event_type_subscribed(self) -> str:
                return another_test_event_type

        DomainEventPublisher.instance().reset()
        DomainEventPublisher.instance().subscribe(TestDomainEventSubscriber())
        DomainEventPublisher.instance().subscribe(AnotherTestDomainEventSubscriber())

        assert TestDomainEventPublisher.event_handled == False
        assert TestDomainEventPublisher.another_event_handled == False

        await DomainEventPublisher.instance().publish(
            TestableDomainEvent(name=event_type)
        ).awaitable()

        assert TestDomainEventPublisher.event_handled == True
        assert TestDomainEventPublisher.another_event_handled == False
