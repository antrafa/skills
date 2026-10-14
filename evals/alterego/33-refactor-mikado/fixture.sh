#!/usr/bin/env bash
set -eu
git init -q -b main
git config user.email dev@example.com
git config user.name "Dev"
mkdir -p src/orders src/infra/oracle test/orders
cat > src/infra/oracle/OracleOrderGateway.java <<'JAVA'
package infra.oracle;

import java.util.List;

public class OracleOrderGateway {
    public List<String> openOrderIds(String customer) {
        return List.of("A-1", "A-2");
    }
    public void markShipped(String orderId) { }
}
JAVA
cat > src/orders/OrderService.java <<'JAVA'
package orders;

import infra.oracle.OracleOrderGateway;
import java.util.List;

public class OrderService {
    private final OracleOrderGateway gateway = new OracleOrderGateway();

    public int shipAll(String customer) {
        List<String> ids = gateway.openOrderIds(customer);
        ids.forEach(gateway::markShipped);
        return ids.size();
    }

    public int getTotal(String customer) {
        return gateway.openOrderIds(customer).size();
    }
}
JAVA
cat > src/orders/OrderReport.java <<'JAVA'
package orders;

public class OrderReport {
    private final OrderService orders = new OrderService();
    public String line(String customer) { return customer + ": " + orders.getTotal(customer); }
}
JAVA
git add -A
git commit -q -m "chore: initial import"
