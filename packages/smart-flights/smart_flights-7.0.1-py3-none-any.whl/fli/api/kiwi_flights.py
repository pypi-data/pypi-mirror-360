"""Kiwi Flights API Integration

Provides access to Kiwi.com's flight search API with focus on hidden city flights.
Supports both one-way and round-trip searches with multi-language and multi-currency support.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
import httpx

from fli.models.google_flights.base import LocalizationConfig, Language, Currency

# Configure logging
logger = logging.getLogger(__name__)

# Kiwi API Configuration
KIWI_GRAPHQL_ENDPOINT = "https://api.skypicker.com/umbrella/v2/graphql"

# Headers for Kiwi API (from kiwi_api_test.py)
KIWI_HEADERS = {
    'content-type': 'application/json',
    'kw-skypicker-visitor-uniqid': 'b500f05c-8234-4a94-82a7-fb5dc02340a9',
    'kw-umbrella-token': '0d23674b463dadee841cc65da51e34fe47bbbe895ae13b69d42ece267c7a2f51',
    'kw-x-rand-id': '07d338ea',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
    'origin': 'https://www.kiwi.com',
    'referer': 'https://www.kiwi.com/cn/search/tiles/--/--/anytime/anytime'
}

# GraphQL Query for One-way Hidden City Flights (使用与 kiwi_api_test.py 相同的完整查询)
ONEWAY_HIDDEN_CITY_QUERY = """
query SearchOneWayItinerariesQuery(
  $search: SearchOnewayInput
  $filter: ItinerariesFilterInput
  $options: ItinerariesOptionsInput
) {
  onewayItineraries(search: $search, filter: $filter, options: $options) {
    __typename
    ... on AppError {
      error: message
    }
    ... on Itineraries {
      server {
        requestId
        packageVersion
        serverToken
      }
      metadata {
        itinerariesCount
        hasMorePending
      }
      itineraries {
        __typename
        ... on ItineraryOneWay {
          id
          shareId
          price {
            amount
            priceBeforeDiscount
          }
          priceEur {
            amount
          }
          provider {
            name
            code
            hasHighProbabilityOfPriceChange
          }
          bagsInfo {
            includedCheckedBags
            includedHandBags
            hasNoBaggageSupported
            hasNoCheckedBaggage
            includedPersonalItem
          }
          bookingOptions {
            edges {
              node {
                token
                bookingUrl
                price {
                  amount
                }
                priceEur {
                  amount
                }
                itineraryProvider {
                  code
                  name
                  hasHighProbabilityOfPriceChange
                }
              }
            }
          }
          travelHack {
            isTrueHiddenCity
            isVirtualInterlining
            isThrowawayTicket
          }
          duration
          pnrCount
          sector {
            id
            duration
            sectorSegments {
              guarantee
              segment {
                id
                source {
                  localTime
                  utcTimeIso
                  station {
                    name
                    code
                    type
                    city {
                      name
                    }
                    country {
                      code
                      name
                    }
                  }
                }
                destination {
                  localTime
                  utcTimeIso
                  station {
                    name
                    code
                    type
                    city {
                      name
                    }
                    country {
                      code
                      name
                    }
                  }
                }
                hiddenDestination {
                  code
                  name
                  city {
                    name
                  }
                  country {
                    code
                    name
                  }
                }
                duration
                type
                code
                carrier {
                  name
                  code
                }
                operatingCarrier {
                  name
                  code
                }
                cabinClass
              }
              layover {
                duration
                isBaggageRecheck
              }
            }
          }
          lastAvailable {
            seatsLeft
          }
        }
      }
    }
  }
}
"""

# GraphQL Query for Round-trip Hidden City Flights
ROUNDTRIP_HIDDEN_CITY_QUERY = """
query SearchReturnHiddenCityQuery(
  $search: SearchReturnInput
  $filter: ItinerariesFilterInput
  $options: ItinerariesOptionsInput
) {
  returnItineraries(search: $search, filter: $filter, options: $options) {
    __typename
    ... on AppError {
      error: message
    }
    ... on Itineraries {
      metadata {
        itinerariesCount
        hasMorePending
      }
      itineraries {
        __typename
        ... on ItineraryReturn {
          id
          price {
            amount
          }
          priceEur {
            amount
          }
          duration
          travelHack {
            isTrueHiddenCity
            isThrowawayTicket
          }
          outbound {
            duration
            sectorSegments {
              segment {
                source {
                  localTime
                  station {
                    name
                    code
                  }
                }
                destination {
                  localTime
                  station {
                    name
                    code
                  }
                }
                hiddenDestination {
                  code
                  name
                }
                duration
                carrier {
                  name
                  code
                }
                code
              }
            }
          }
          inbound {
            duration
            sectorSegments {
              segment {
                source {
                  localTime
                  station {
                    name
                    code
                  }
                }
                destination {
                  localTime
                  station {
                    name
                    code
                  }
                }
                hiddenDestination {
                  code
                  name
                }
                duration
                carrier {
                  name
                  code
                }
                code
              }
            }
          }
        }
      }
    }
  }
}
"""


class KiwiFlightsAPI:
    """Kiwi Flights API client for hidden city flight searches."""
    
    def __init__(self, localization_config: LocalizationConfig = None):
        """Initialize the Kiwi API client.
        
        Args:
            localization_config: Configuration for language and currency settings
        """
        self.localization_config = localization_config or LocalizationConfig()
        self.headers = KIWI_HEADERS.copy()
        self.timeout = 30.0
    
    def _build_search_variables(self, origin: str, destination: str,
                               departure_date: str, adults: int = 1, cabin_class: str = "ECONOMY",
                               limit: int = 50, hidden_city_only: bool = False) -> Dict[str, Any]:
        """Build search variables for Kiwi API request - 基于真实浏览器请求负载.

        Args:
            origin: Origin airport code (e.g., 'PEK')
            destination: Destination airport code (e.g., 'LAX')
            departure_date: Departure date in YYYY-MM-DD format
            adults: Number of adult passengers
            cabin_class: Cabin class ('ECONOMY', 'BUSINESS', 'FIRST')
            limit: Maximum number of results to return
            hidden_city_only: If True, enable hidden city specific filters. If False, search all flight types.

        Returns:
            Dictionary containing search variables
        """
        dep_date_obj = datetime.strptime(departure_date, "%Y-%m-%d")

        # Map localization config to Kiwi API parameters
        currency_code = "cny" if self.localization_config.currency == Currency.CNY else "usd"
        locale_code = "cn" if self.localization_config.language == Language.CHINESE else "en"  # 使用 'cn' 而不是 'zh'
        partner_market = "cn" if self.localization_config.language == Language.CHINESE else "us"

        return {
            "search": {
                "itinerary": {
                    "source": {"ids": [f"Station:airport:{origin.upper()}"]},
                    "destination": {"ids": [f"Station:airport:{destination.upper()}"]},
                    "outboundDepartureDate": {
                        "start": dep_date_obj.strftime("%Y-%m-%dT00:00:00"),
                        "end": dep_date_obj.strftime("%Y-%m-%dT23:59:59")
                    }
                },
                "passengers": {
                    "adults": adults,
                    "children": 0,
                    "infants": 0,
                    "adultsHoldBags": [0] * adults,  # 每个成人的托运行李数量
                    "adultsHandBags": [0] * adults,  # 每个成人的手提行李数量
                    "childrenHoldBags": [],
                    "childrenHandBags": []
                },
                "cabinClass": {
                    "cabinClass": cabin_class,
                    "applyMixedClasses": False
                }
            },
            "filter": {
                "allowChangeInboundDestination": True,
                "allowChangeInboundSource": True,
                "allowDifferentStationConnection": True,
                "enableSelfTransfer": True,
                # 动态控制隐藏城市相关过滤器
                "enableThrowAwayTicketing": hidden_city_only,  # 只在隐藏城市模式下启用
                "enableTrueHiddenCity": hidden_city_only,  # 只在隐藏城市模式下启用
                "maxStopsCount": 1,  # 搜索直飞和1次中转航班
                "transportTypes": ["FLIGHT"],
                # 动态设置内容提供商：目前只支持KIWI
                "contentProviders": ["KIWI"],
                "flightsApiLimit": 25,  # 关键：API限制
                "limit": limit  # 关键：结果限制，动态设置
            },
            "options": {
                "sortBy": "QUALITY",  # 修正为 QUALITY 而不是 PRICE
                "mergePriceDiffRule": "INCREASED",
                "currency": currency_code,
                "apiUrl": None,
                "locale": locale_code,
                "market": "us",
                "partner": "skypicker",
                "partnerMarket": partner_market,
                "affilID": "cj_5250933",  # 关键：联盟ID
                "storeSearch": False,
                "searchStrategy": "REDUCED",
                "abTestInput": {},  # 简化A/B测试参数，避免无效字段
                "serverToken": None,
                "searchSessionId": None
            }
        }

    def _build_roundtrip_variables(self, origin: str, destination: str,
                                  departure_date: str, return_date: str,
                                  adults: int = 1, cabin_class: str = "ECONOMY",
                                  hidden_city_only: bool = False) -> Dict[str, Any]:
        """Build search variables for round-trip Kiwi API request - 基于成功的单程请求负载模式.

        Args:
            origin: Origin airport code
            destination: Destination airport code
            departure_date: Departure date in YYYY-MM-DD format
            return_date: Return date in YYYY-MM-DD format
            adults: Number of adult passengers
            cabin_class: Cabin class ('ECONOMY', 'BUSINESS', 'FIRST')
            hidden_city_only: If True, enable hidden city specific filters. If False, search all flight types.

        Returns:
            Dictionary containing search variables
        """
        # 复用单程的构建逻辑作为基础，传递hidden_city_only参数
        variables = self._build_search_variables(origin, destination, departure_date, adults, cabin_class, hidden_city_only=hidden_city_only)

        # 添加返程日期
        ret_date_obj = datetime.strptime(return_date, "%Y-%m-%d")
        variables["search"]["itinerary"]["inboundDepartureDate"] = {
            "start": ret_date_obj.strftime("%Y-%m-%dT00:00:00"),
            "end": ret_date_obj.strftime("%Y-%m-%dT23:59:59")
        }

        # 添加往返特有的过滤器参数
        variables["filter"]["allowReturnFromDifferentCity"] = True
        variables["filter"]["allowChangeInboundDestination"] = True
        variables["filter"]["allowChangeInboundSource"] = True

        return variables

    async def search_oneway_hidden_city(self, origin: str, destination: str,
                                       departure_date: str, adults: int = 1,
                                       limit: int = 50, cabin_class: str = "ECONOMY",
                                       enable_pagination: bool = True, max_pages: int = 10,
                                       hidden_city_only: bool = False) -> Dict[str, Any]:
        """Search for one-way flights with automatic pagination.

        Args:
            origin: Origin airport code (e.g., 'PEK')
            destination: Destination airport code (e.g., 'LAX')
            departure_date: Departure date in YYYY-MM-DD format
            adults: Number of adult passengers
            limit: Maximum number of results per page (default: 50)
            cabin_class: Cabin class ('ECONOMY', 'BUSINESS', 'FIRST')
            enable_pagination: Whether to automatically fetch all pages (default: True)
            max_pages: Maximum number of pages to fetch (default: 10)
            hidden_city_only: If True, search only hidden city flights. If False, search all flight types.

        Returns:
            Dictionary containing search results and metadata from all pages
        """
        search_id = f"oneway_hidden_{int(time.time())}"
        logger.info(f"[{search_id}] Searching one-way hidden city flights: {origin} -> {destination}")

        try:
            # Build search variables with hidden_city_only parameter
            variables = self._build_search_variables(origin, destination, departure_date, adults, cabin_class, limit, hidden_city_only)

            # 使用支持分页的查询以获得完整的航班结果
            paginated_query = """
query SearchItinerariesQuery(
  $search: SearchOnewayInput
  $filter: ItinerariesFilterInput
  $options: ItinerariesOptionsInput
) {
  onewayItineraries(search: $search, filter: $filter, options: $options) {
    __typename
    ... on AppError {
      error: message
    }
    ... on Itineraries {
      server {
        requestId
        environment
        packageVersion
        serverToken
      }
      metadata {
        itinerariesCount
        hasMorePending
      }
      itineraries {
        __typename
        ... on ItineraryOneWay {
          id
          price {
            amount
          }
          priceEur {
            amount
          }
          duration
          travelHack {
            isTrueHiddenCity
            isThrowawayTicket
          }
          sector {
            sectorSegments {
              segment {
                source {
                  localTime
                  station {
                    code
                    name
                  }
                }
                destination {
                  localTime
                  station {
                    code
                    name
                  }
                }
                hiddenDestination {
                  code
                  name
                }
                carrier {
                  code
                  name
                }
                code
                duration
              }
            }
          }
        }
      }
    }
  }
}
"""

            payload = {
                "query": paginated_query,
                "variables": variables
            }

            # Send request
            api_url = f"{KIWI_GRAPHQL_ENDPOINT}?featureName=SearchOneWayItinerariesQuery"

            # 根据是否启用分页选择不同的处理方式
            if enable_pagination:
                return await self._search_with_pagination(
                    paginated_query, variables, search_id, limit, max_pages
                )
            else:
                # 传统的单页搜索
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(api_url, headers=self.headers, json=payload)

                    logger.info(f"[{search_id}] Response status: {response.status_code}")

                    if response.status_code == 200:
                        response_data = response.json()
                        return self._parse_oneway_response(response_data, search_id, limit)
                    else:
                        logger.error(f"[{search_id}] Request failed: {response.status_code} - {response.text}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status_code}",
                            "details": response.text
                        }

        except Exception as e:
            logger.error(f"[{search_id}] Search failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def search_roundtrip_hidden_city(self, origin: str, destination: str,
                                          departure_date: str, return_date: str,
                                          adults: int = 1, limit: int = 50, cabin_class: str = "ECONOMY",
                                          hidden_city_only: bool = False) -> Dict[str, Any]:
        """Search for round-trip flights.

        Args:
            origin: Origin airport code
            destination: Destination airport code
            departure_date: Departure date in YYYY-MM-DD format
            return_date: Return date in YYYY-MM-DD format
            adults: Number of adult passengers
            limit: Maximum number of results to return
            cabin_class: Cabin class ('ECONOMY', 'BUSINESS', 'FIRST')
            hidden_city_only: If True, search only hidden city flights. If False, search all flight types.

        Returns:
            Dictionary containing search results and metadata
        """
        search_id = f"roundtrip_hidden_{int(time.time())}"
        logger.info(f"[{search_id}] Searching round-trip hidden city flights: {origin} ⇄ {destination}")

        try:
            # Build search variables with hidden_city_only parameter
            variables = self._build_roundtrip_variables(origin, destination, departure_date, return_date, adults, cabin_class, hidden_city_only)

            payload = {
                "query": ROUNDTRIP_HIDDEN_CITY_QUERY,
                "variables": variables
            }

            # Send request
            api_url = f"{KIWI_GRAPHQL_ENDPOINT}?featureName=SearchReturnItinerariesQuery"

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(api_url, headers=self.headers, json=payload)

                logger.info(f"[{search_id}] Response status: {response.status_code}")

                if response.status_code == 200:
                    response_data = response.json()
                    return self._parse_roundtrip_response(response_data, search_id, limit)
                else:
                    logger.error(f"[{search_id}] Request failed: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                        "details": response.text
                    }

        except Exception as e:
            logger.error(f"[{search_id}] Search failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _parse_oneway_response(self, response_data: Dict[str, Any],
                              search_id: str, limit: int) -> Dict[str, Any]:
        """Parse one-way flight search response.

        Args:
            response_data: Raw response from Kiwi API
            search_id: Search identifier for logging
            limit: Maximum number of results to return

        Returns:
            Parsed response with flight information
        """
        try:
            if 'data' not in response_data:
                return {
                    "success": False,
                    "error": "Missing data field in response",
                    "raw_response": response_data
                }

            oneway_data = response_data['data'].get('onewayItineraries')
            if not oneway_data:
                return {
                    "success": False,
                    "error": "Missing onewayItineraries field in response",
                    "raw_response": response_data
                }

            # Check for API errors
            if oneway_data.get('__typename') == 'AppError':
                error_msg = oneway_data.get('error', 'Unknown API error')
                logger.error(f"[{search_id}] API returned error: {error_msg}")
                return {
                    "success": False,
                    "error": f"API Error: {error_msg}"
                }

            if oneway_data.get('__typename') != 'Itineraries':
                return {
                    "success": False,
                    "error": f"Unexpected response type: {oneway_data.get('__typename')}",
                    "raw_response": response_data
                }

            # Parse flight data
            itineraries = oneway_data.get('itineraries', [])
            metadata = oneway_data.get('metadata', {})

            logger.info(f"[{search_id}] Found {len(itineraries)} flights")

            # Parse all flights and count hidden city ones
            all_flights = []
            hidden_city_count = 0
            for itinerary in itineraries[:limit]:
                flight_info = self._extract_oneway_flight_info(itinerary)
                if flight_info:
                    all_flights.append(flight_info)
                    if flight_info.get('is_hidden_city'):
                        hidden_city_count += 1

            return {
                "success": True,
                "search_id": search_id,
                "trip_type": "oneway",
                "total_count": metadata.get('itinerariesCount', 0),
                "hidden_city_count": hidden_city_count,
                "has_more": metadata.get('hasMorePending', False),
                "flights": all_flights,
                "currency": self.localization_config.currency.value,
                "language": self.localization_config.language.value
            }

        except Exception as e:
            logger.error(f"[{search_id}] Failed to parse response: {e}")
            return {
                "success": False,
                "error": f"Parse failed: {str(e)}",
                "raw_response": response_data
            }

    def _parse_roundtrip_response(self, response_data: Dict[str, Any],
                                 search_id: str, limit: int) -> Dict[str, Any]:
        """Parse round-trip flight search response.

        Args:
            response_data: Raw response from Kiwi API
            search_id: Search identifier for logging
            limit: Maximum number of results to return

        Returns:
            Parsed response with flight information
        """
        try:
            if 'data' not in response_data:
                return {
                    "success": False,
                    "error": "Missing data field in response",
                    "raw_response": response_data
                }

            return_data = response_data['data'].get('returnItineraries')
            if not return_data:
                return {
                    "success": False,
                    "error": "Missing returnItineraries field in response",
                    "raw_response": response_data
                }

            # Check for API errors
            if return_data.get('__typename') == 'AppError':
                error_msg = return_data.get('error', 'Unknown API error')
                logger.error(f"[{search_id}] API returned error: {error_msg}")
                return {
                    "success": False,
                    "error": f"API Error: {error_msg}"
                }

            if return_data.get('__typename') != 'Itineraries':
                return {
                    "success": False,
                    "error": f"Unexpected response type: {return_data.get('__typename')}",
                    "raw_response": response_data
                }

            # Parse flight data
            itineraries = return_data.get('itineraries', [])
            metadata = return_data.get('metadata', {})

            logger.info(f"[{search_id}] Found {len(itineraries)} round-trip flights")

            # Parse all flights and count hidden city ones
            all_flights = []
            hidden_city_count = 0
            for itinerary in itineraries[:limit]:
                flight_info = self._extract_roundtrip_flight_info(itinerary)
                if flight_info:
                    all_flights.append(flight_info)
                    if flight_info.get('is_hidden_city'):
                        hidden_city_count += 1

            return {
                "success": True,
                "search_id": search_id,
                "trip_type": "roundtrip",
                "total_count": metadata.get('itinerariesCount', 0),
                "hidden_city_count": hidden_city_count,
                "has_more": metadata.get('hasMorePending', False),
                "flights": all_flights,
                "currency": self.localization_config.currency.value,
                "language": self.localization_config.language.value
            }

        except Exception as e:
            logger.error(f"[{search_id}] Failed to parse response: {e}")
            return {
                "success": False,
                "error": f"Parse failed: {str(e)}",
                "raw_response": response_data
            }

    def _extract_oneway_flight_info(self, itinerary: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract key information from one-way flight itinerary.

        Args:
            itinerary: Flight itinerary data from API

        Returns:
            Extracted flight information or None if extraction fails
        """
        try:
            # Basic information
            flight_id = itinerary.get('id', '')
            price_main = itinerary.get('price', {}).get('amount', 0)
            price_eur = itinerary.get('priceEur', {}).get('amount', 0)
            duration = itinerary.get('duration', 0)

            # Hidden city information
            travel_hack = itinerary.get('travelHack', {})
            is_hidden_city = travel_hack.get('isTrueHiddenCity', False)
            is_throwaway = travel_hack.get('isThrowawayTicket', False)

            # Flight segments information
            sector = itinerary.get('sector', {})
            segments = sector.get('sectorSegments', [])

            if not segments:
                return None

            # Extract first and last segments for complete route info
            first_segment = segments[0].get('segment', {})
            last_segment = segments[-1].get('segment', {})

            # Source from first segment, destination from last segment
            source = first_segment.get('source', {})
            destination = last_segment.get('destination', {})

            # Use adaptive hidden destination parsing
            hidden_destination = self._find_hidden_destination(segments)

            # Use first segment's carrier for main airline
            carrier = first_segment.get('carrier', {})

            # Get localized names
            airline_name = self.localization_config.get_airline_name(
                carrier.get('code', ''), carrier.get('name', '')
            )

            # Extract complete route information
            route_info = self._extract_complete_route_info(segments)

            return {
                "id": flight_id,
                "price": price_main,
                "price_eur": price_eur,
                "currency": self.localization_config.currency.value,
                "currency_symbol": self.localization_config.currency_symbol,
                "duration": duration // 60 if duration else 0,  # 转换秒到分钟
                "duration_minutes": duration // 60 if duration else 0,
                "is_hidden_city": is_hidden_city,
                "is_throwaway": is_throwaway,
                "departure_airport": source.get('station', {}).get('code', ''),
                "departure_airport_name": self.localization_config.get_airport_name(
                    source.get('station', {}).get('code', ''),
                    source.get('station', {}).get('name', '')
                ),
                "arrival_airport": destination.get('station', {}).get('code', ''),
                "arrival_airport_name": self.localization_config.get_airport_name(
                    destination.get('station', {}).get('code', ''),
                    destination.get('station', {}).get('name', '')
                ),
                "hidden_destination_code": hidden_destination.get('code', '') if hidden_destination else '',
                "hidden_destination_name": self.localization_config.get_airport_name(
                    hidden_destination.get('code', ''), hidden_destination.get('name', '')
                ) if hidden_destination else '',
                "carrier_code": carrier.get('code', ''),
                "carrier_name": airline_name,
                "flight_number": first_segment.get('code', ''),
                "departure_time": source.get('localTime', ''),
                "arrival_time": destination.get('localTime', ''),
                "segment_count": len(segments),
                "route_segments": route_info.get('segments', []),  # 完整航段信息
                "trip_type": "oneway"
            }

        except Exception as e:
            logger.error(f"Failed to extract one-way flight info: {e}")
            return None

    def _extract_roundtrip_flight_info(self, itinerary: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract key information from round-trip flight itinerary.

        Args:
            itinerary: Flight itinerary data from API

        Returns:
            Extracted flight information or None if extraction fails
        """
        try:
            # Basic information
            flight_id = itinerary.get('id', '')
            price_main = itinerary.get('price', {}).get('amount', 0)
            price_eur = itinerary.get('priceEur', {}).get('amount', 0)
            duration = itinerary.get('duration', 0)

            # Hidden city information
            travel_hack = itinerary.get('travelHack', {})
            is_hidden_city = travel_hack.get('isTrueHiddenCity', False)
            is_throwaway = travel_hack.get('isThrowawayTicket', False)

            # Parse outbound and inbound legs
            def parse_leg(leg_data: Dict[str, Any], leg_type: str) -> Optional[Dict[str, Any]]:
                segments = leg_data.get('sectorSegments', [])
                if not segments:
                    return None

                # For simplicity, take the first segment
                segment = segments[0].get('segment', {})
                source = segment.get('source', {})
                destination = segment.get('destination', {})
                hidden_destination = segment.get('hiddenDestination', {})
                carrier = segment.get('carrier', {})

                # Get localized names
                airline_name = self.localization_config.get_airline_name(
                    carrier.get('code', ''), carrier.get('name', '')
                )

                return {
                    "departure_airport": source.get('station', {}).get('code', ''),
                    "departure_airport_name": self.localization_config.get_airport_name(
                        source.get('station', {}).get('code', ''),
                        source.get('station', {}).get('name', '')
                    ),
                    "arrival_airport": destination.get('station', {}).get('code', ''),
                    "arrival_airport_name": self.localization_config.get_airport_name(
                        destination.get('station', {}).get('code', ''),
                        destination.get('station', {}).get('name', '')
                    ),
                    "hidden_destination_code": hidden_destination.get('code', '') if hidden_destination else '',
                    "hidden_destination_name": hidden_destination.get('name', '') if hidden_destination else '',
                    "carrier_code": carrier.get('code', ''),
                    "carrier_name": airline_name,
                    "flight_number": segment.get('code', ''),
                    "departure_time": source.get('localTime', ''),
                    "arrival_time": destination.get('localTime', ''),
                    "duration": segment.get('duration', 0),
                    "is_hidden": bool(hidden_destination),
                    "leg_type": leg_type
                }

            outbound_info = parse_leg(itinerary.get('outbound', {}), "outbound")
            inbound_info = parse_leg(itinerary.get('inbound', {}), "inbound")

            if not outbound_info or not inbound_info:
                return None

            return {
                "id": flight_id,
                "price": price_main,
                "price_eur": price_eur,
                "currency": self.localization_config.currency.value,
                "currency_symbol": self.localization_config.currency_symbol,
                "duration_minutes": duration // 60 if duration else 0,
                "is_hidden_city": is_hidden_city,
                "is_throwaway": is_throwaway,
                "outbound": outbound_info,
                "inbound": inbound_info,
                "trip_type": "roundtrip"
            }

        except Exception as e:
            logger.error(f"Failed to extract round-trip flight info: {e}")
            return None

    def _find_hidden_destination(self, segments: list) -> dict:
        """Adaptively find hidden destination information in flight segments.

        Different query types may have hidden destination in different locations:
        - Economy vs Business class
        - Direct vs connecting flights
        - Different routes

        Args:
            segments: List of flight segments

        Returns:
            Hidden destination information or empty dict if not found
        """
        if not segments:
            return {}

        # Strategy 1: Check all segments for hidden destination (most common)
        for seg in segments:
            segment_data = seg.get('segment', {})
            hidden_dest = segment_data.get('hiddenDestination')
            if hidden_dest:
                return hidden_dest

        # Strategy 2: Check if any segment has a different final destination
        # This handles cases where hidden city info might be implicit
        if len(segments) > 1:
            last_segment = segments[-1].get('segment', {})
            last_destination = last_segment.get('destination', {})

            # Check if the last segment's destination differs from expected
            # This is a fallback for cases where hiddenDestination field is missing
            for i, seg in enumerate(segments[:-1]):
                segment_data = seg.get('segment', {})
                dest = segment_data.get('destination', {})
                if dest and dest != last_destination:
                    # Potential hidden city scenario
                    return dest.get('station', {})

        return {}

    def _extract_complete_route_info(self, segments: list) -> dict:
        """Extract complete route information including all segments.

        Args:
            segments: List of flight segments

        Returns:
            Dictionary with complete route information
        """
        if not segments:
            return {}

        first_segment = segments[0].get('segment', {})
        last_segment = segments[-1].get('segment', {})

        # Build complete route
        route_segments = []
        for seg in segments:
            segment_data = seg.get('segment', {})
            source = segment_data.get('source', {})
            destination = segment_data.get('destination', {})

            route_segments.append({
                "from": source.get('station', {}).get('code', ''),
                "to": destination.get('station', {}).get('code', ''),
                "carrier": segment_data.get('carrier', {}).get('code', ''),
                "flight_number": segment_data.get('code', ''),
                "departure_time": source.get('localTime', ''),
                "arrival_time": destination.get('localTime', ''),
                "duration": segment_data.get('duration', 0)
            })

        return {
            "origin": first_segment.get('source', {}).get('station', {}).get('code', ''),
            "destination": last_segment.get('destination', {}).get('station', {}).get('code', ''),
            "segments": route_segments,
            "total_segments": len(segments)
        }

    def _detect_query_type(self, variables: dict) -> str:
        """Detect the type of query to apply appropriate parsing strategy.

        Args:
            variables: Query variables sent to API

        Returns:
            Query type string for parsing strategy selection
        """
        cabin_class = variables.get('search', {}).get('cabinClass', {}).get('cabinClass', 'ECONOMY')
        max_stops = variables.get('filter', {}).get('maxStopsCount', 0)
        has_return = 'inboundDepartureDate' in variables.get('search', {}).get('itinerary', {})

        query_type = f"{cabin_class.lower()}"
        if max_stops > 0:
            query_type += f"_stops{max_stops}"
        if has_return:
            query_type += "_roundtrip"
        else:
            query_type += "_oneway"

        return query_type

    async def _search_with_pagination(
        self,
        query: str,
        base_variables: Dict[str, Any],
        search_id: str,
        limit: int,
        max_pages: int
    ) -> Dict[str, Any]:
        """执行分页搜索以获取所有可用航班

        Args:
            query: GraphQL查询字符串
            base_variables: 基础查询变量
            search_id: 搜索ID用于日志
            limit: 每页限制数量
            max_pages: 最大页数

        Returns:
            包含所有页面航班数据的字典
        """
        all_flights = []
        all_flight_ids = set()  # 用于去重
        page_count = 0
        server_token = None
        total_api_count = 0
        hidden_city_count = 0

        logger.info(f"[{search_id}] Starting paginated search (max_pages: {max_pages})")

        try:
            api_url = f"{KIWI_GRAPHQL_ENDPOINT}?featureName=SearchItinerariesQuery"

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                while page_count < max_pages:
                    page_count += 1
                    logger.info(f"[{search_id}] Fetching page {page_count}")

                    # 准备当前页的变量 - 使用深拷贝避免引用问题
                    current_variables = {
                        "search": base_variables["search"].copy(),
                        "filter": base_variables["filter"].copy(),
                        "options": base_variables["options"].copy()
                    }
                    current_variables["options"]["serverToken"] = server_token

                    payload = {
                        "query": query,
                        "variables": current_variables
                    }

                    # 发送请求
                    response = await client.post(api_url, headers=self.headers, json=payload)

                    if response.status_code != 200:
                        logger.error(f"[{search_id}] Page {page_count} failed: {response.status_code}")
                        break

                    response_data = response.json()

                    # 检查响应格式
                    if 'data' not in response_data or 'onewayItineraries' not in response_data['data']:
                        logger.error(f"[{search_id}] Page {page_count} invalid response format")
                        if 'errors' in response_data:
                            logger.error(f"[{search_id}] GraphQL errors: {response_data['errors']}")
                        break

                    itineraries_data = response_data['data']['onewayItineraries']

                    # 检查API错误
                    if itineraries_data.get('__typename') == 'AppError':
                        logger.error(f"[{search_id}] API error: {itineraries_data.get('error', 'Unknown')}")
                        break

                    # 获取数据
                    itineraries = itineraries_data.get('itineraries', [])
                    metadata = itineraries_data.get('metadata', {})
                    server_info = itineraries_data.get('server', {})

                    # 更新总计数（只在第一页设置）
                    if page_count == 1:
                        total_api_count = metadata.get('itinerariesCount', 0)

                    logger.info(f"[{search_id}] Page {page_count}: {len(itineraries)} flights")

                    # 处理航班数据
                    page_new_flights = 0
                    for itinerary in itineraries:
                        flight_info = self._extract_oneway_flight_info(itinerary)
                        if flight_info:
                            flight_id = flight_info.get('id', '')
                            # 去重检查
                            if flight_id and flight_id not in all_flight_ids:
                                all_flight_ids.add(flight_id)
                                all_flights.append(flight_info)
                                page_new_flights += 1

                                if flight_info.get('is_hidden_city'):
                                    hidden_city_count += 1

                    logger.info(f"[{search_id}] Page {page_count}: {page_new_flights} new unique flights")

                    # 检查是否有serverToken继续分页
                    # 注意：忽略hasMorePending，因为KIWI API可能返回false但仍有更多数据
                    has_more = metadata.get('hasMorePending', False)
                    new_server_token = server_info.get('serverToken')

                    logger.info(f"[{search_id}] hasMorePending: {has_more}, serverToken: {'有' if new_server_token else '无'}")

                    if not new_server_token:
                        logger.info(f"[{search_id}] No serverToken received, stopping pagination")
                        break

                    # 如果没有新的航班且已经获取了多页，停止分页
                    if page_new_flights == 0 and page_count > 1:
                        logger.info(f"[{search_id}] No new flights on page {page_count}, stopping pagination")
                        break

                    # 更新token用于下一页
                    server_token = new_server_token

                    # 避免请求过快
                    await asyncio.sleep(1)

            logger.info(f"[{search_id}] Pagination complete: {len(all_flights)} unique flights from {page_count} pages")

            return {
                "success": True,
                "search_id": search_id,
                "trip_type": "oneway",
                "total_count": total_api_count,
                "hidden_city_count": hidden_city_count,
                "has_more": False,  # 分页完成后设为False
                "flights": all_flights,
                "pagination_info": {
                    "pages_fetched": page_count,
                    "max_pages": max_pages,
                    "unique_flights": len(all_flights),
                    "total_flights_processed": sum(len(page.get('itineraries', [])) for page in [])
                }
            }

        except Exception as e:
            logger.error(f"[{search_id}] Pagination failed: {e}")
            return {
                "success": False,
                "error": f"Pagination error: {str(e)}",
                "flights": all_flights,  # 返回已获取的航班
                "pagination_info": {
                    "pages_fetched": page_count,
                    "error_on_page": page_count + 1 if page_count < max_pages else None
                }
            }


# Global instance for easy access
kiwi_flights_api = KiwiFlightsAPI()
