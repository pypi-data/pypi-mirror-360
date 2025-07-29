#!/usr/bin/env python3
"""Example usage of py-nycmta package"""

from py_nycmta import Train


def main():
    """Demonstrate the simplified package usage"""

    print("🚇 py-nycmta Package Demo")
    print("=" * 30)

    # Create train instances for different lines
    trains = {
        "F": Train("F"),
        "N": Train("N"),
        "1": Train("1"),
        "A": Train("A"),
        "L": Train("L"),
    }

    # Show train info
    print("\n📋 Available trains:")
    for _train_id, train in trains.items():
        print(f"  {train} - Feed: {train.feed_url.split('/')[-1]}")

    # Example of getting arrivals (would require network)
    print("\n💡 Example usage:")
    print("from py_nycmta import Train")
    print("")
    print("# Create a train instance")
    print("f_train = Train('F')")
    print("")
    print("# Get arrivals at 7 Av")
    print("arrivals = f_train.get_arrivals('F24')")
    print("")
    print("# Print arrival information")
    print("for arrival in arrivals:")
    print("    print(f'{arrival.train_id} train in {arrival.minutes_away} mins')")

    print("\n✅ Package successfully simplified!")
    print("   - Only 1 class to import: Train")
    print("   - Works with all 22 subway lines")
    print("   - Minimal dependencies: httpx, protobuf, gtfs-realtime-bindings")


if __name__ == "__main__":
    main()
