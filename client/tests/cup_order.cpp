#include <SlotExpansion/CupOrder.hpp>
#include <cassert>
#include <iostream>
#include <vector>

static void Check(unsigned int count, int malformed) {
    const unsigned short guard = 0xABCD;
    std::vector<unsigned short> input(count), order(count + 2, guard), inverse(count + 2, guard);
    for (unsigned int i = 0; i < count; ++i) input[i] = count - 1 - i;
    if (malformed == 1) input[0] = count;
    if (malformed == 2) input[0] = input[1];
    const bool ok = Pulsar::BuildCupOrder(input.data(), count, order.data() + 1, inverse.data() + 1);
    assert(ok == (malformed == 0));
    assert(order.front() == guard && order.back() == guard);
    assert(inverse.front() == guard && inverse.back() == guard);
    for (unsigned int i = 0; i < count; ++i) {
        assert(order[i + 1] == (malformed ? i : count - i - 1));
        assert(inverse[order[i + 1] + 1] == i);
    }
}

int main() {
    const unsigned int sizes[] = {0, 4, 8, 88, 96, 108, 112, 352, 400};
    for (unsigned int i = 0; i < sizeof(sizes) / sizeof(sizes[0]); ++i) {
        Check(sizes[i], 0);
        if (sizes[i] > 1) { Check(sizes[i], 1); Check(sizes[i], 2); }
    }
    // Read the real config's alphabetical table from stdin as well.
    unsigned int count;
    assert(static_cast<bool>(std::cin >> count));
    std::vector<unsigned short> source(count), order(count), inverse(count);
    for (unsigned int i = 0; i < count; ++i) {
        unsigned int value;
        assert(static_cast<bool>(std::cin >> value));
        source[i] = value;
    }
    assert(Pulsar::BuildCupOrder(source.data(), count, order.data(), inverse.data()));
    for (unsigned int i = 0; i < count; ++i) {
        assert(order[i] == source[i]);
        assert(inverse[order[i]] == i);
    }
    std::cout << "PASS: 25 synthetic cup-order cases and real config permutation\n";
}
