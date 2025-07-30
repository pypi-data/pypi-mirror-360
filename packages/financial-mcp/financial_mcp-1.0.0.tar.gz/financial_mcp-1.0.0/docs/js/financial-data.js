// Financial Data Manager for Dashboard
// This module handles data loading and processing for the financial dashboard

class FinancialDataManager {
    constructor() {
        this.assets = ['SP500', 'Gold', 'Bitcoin', 'Ethereum', 'XRP'];
        this.colors = {
            'SP500': '#1f77b4',
            'Gold': '#ff7f0e', 
            'Bitcoin': '#f39c12',
            'Ethereum': '#9b59b6',
            'XRP': '#e74c3c'
        };
        this.data = null;
    }

    // Load real data from CSV files (when available)
    async loadRealData() {
        try {
            // In a real implementation, you would fetch from the actual CSV files
            const responses = await Promise.all([
                fetch('./data/SP500_daily_returns_2020_2024.csv'),
                fetch('./data/Gold_daily_returns_2020_2024.csv'),
                fetch('./data/BTC_daily_returns_2020_2024.csv'),
                fetch('./data/ETH_daily_returns_2020_2024.csv'),
                fetch('./data/XRP_daily_returns_2020_2024.csv')
            ]);

            const csvData = await Promise.all(responses.map(r => r.text()));
            return this.parseCSVData(csvData);
        } catch (error) {
            console.log('Real data not available, using sample data');
            return this.generateSampleData();
        }
    }

    parseCSVData(csvData) {
        const parsedData = {};
        
        csvData.forEach((csv, index) => {
            const asset = this.assets[index];
            const lines = csv.split('\n');
            const headers = lines[0].split(',');
            
            parsedData[asset] = {
                dates: [],
                prices: [],
                returns: [],
                cumulativeReturns: []
            };

            let cumulativeReturn = 1;
            
            for (let i = 1; i < lines.length; i++) {
                const values = lines[i].split(',');
                if (values.length >= 3) {
                    const date = values[0];
                    const price = parseFloat(values[1]);
                    const dailyReturn = parseFloat(values[2]);
                    
                    cumulativeReturn *= (1 + dailyReturn / 100);
                    
                    parsedData[asset].dates.push(date);
                    parsedData[asset].prices.push(price);
                    parsedData[asset].returns.push(dailyReturn);
                    parsedData[asset].cumulativeReturns.push((cumulativeReturn - 1) * 100);
                }
            }
        });

        return parsedData;
    }

    // Generate realistic sample data for demonstration
    generateSampleData() {
        const data = {};
        const startDate = new Date('2020-01-01');
        const endDate = new Date('2024-12-31');
        const totalDays = Math.floor((endDate - startDate) / (1000 * 60 * 60 * 24));

        this.assets.forEach(asset => {
            data[asset] = {
                dates: [],
                prices: [],
                returns: [],
                cumulativeReturns: []
            };

            // Starting prices based on realistic values
            let price = this.getStartingPrice(asset);
            let cumulativeReturn = 1;

            for (let i = 0; i <= totalDays; i++) {
                const date = new Date(startDate.getTime() + i * 24 * 60 * 60 * 1000);
                
                // Skip weekends for traditional assets
                if (this.isWeekend(asset, date)) {
                    continue;
                }

                const { volatility, drift } = this.getAssetParameters(asset);
                const dailyReturn = this.generateDailyReturn(volatility, drift);
                
                price = price * (1 + dailyReturn);
                cumulativeReturn = cumulativeReturn * (1 + dailyReturn);

                data[asset].dates.push(date.toISOString().split('T')[0]);
                data[asset].prices.push(price);
                data[asset].returns.push(dailyReturn * 100);
                data[asset].cumulativeReturns.push((cumulativeReturn - 1) * 100);
            }
        });

        return data;
    }

    getStartingPrice(asset) {
        const startingPrices = {
            'Bitcoin': 7000,
            'Ethereum': 130,
            'XRP': 0.2,
            'Gold': 1500,
            'SP500': 3200
        };
        return startingPrices[asset];
    }

    isWeekend(asset, date) {
        return (asset === 'SP500' || asset === 'Gold') && 
               (date.getDay() === 0 || date.getDay() === 6);
    }

    getAssetParameters(asset) {
        const parameters = {
            'Bitcoin': { volatility: 0.04, drift: 0.0003 },
            'Ethereum': { volatility: 0.05, drift: 0.0004 },
            'XRP': { volatility: 0.06, drift: 0.0001 },
            'Gold': { volatility: 0.012, drift: 0.00015 },
            'SP500': { volatility: 0.015, drift: 0.0002 }
        };
        return parameters[asset];
    }

    generateDailyReturn(volatility, drift) {
        // Generate returns using a more realistic model with occasional large moves
        const random = Math.random();
        
        // 95% of the time, normal distribution
        if (random < 0.95) {
            return this.normalRandom() * volatility + drift;
        }
        // 5% of the time, larger moves (fat tails)
        else {
            return this.normalRandom() * volatility * 3 + drift;
        }
    }

    normalRandom() {
        // Box-Muller transformation for normal distribution
        const u1 = Math.random();
        const u2 = Math.random();
        return Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
    }

    // Calculate correlation between two return series
    calculateCorrelation(returns1, returns2) {
        const n = Math.min(returns1.length, returns2.length);
        const x = returns1.slice(0, n);
        const y = returns2.slice(0, n);
        
        const sumX = x.reduce((a, b) => a + b, 0);
        const sumY = y.reduce((a, b) => a + b, 0);
        const sumXY = x.reduce((sum, xi, i) => sum + xi * y[i], 0);
        const sumX2 = x.reduce((sum, xi) => sum + xi * xi, 0);
        const sumY2 = y.reduce((sum, yi) => sum + yi * yi, 0);

        const numerator = n * sumXY - sumX * sumY;
        const denominator = Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY));

        return denominator === 0 ? 0 : numerator / denominator;
    }

    // Calculate rolling volatility
    calculateRollingVolatility(returns, window = 30) {
        const rollingVol = [];
        
        for (let i = window - 1; i < returns.length; i++) {
            const windowReturns = returns.slice(i - window + 1, i + 1);
            const mean = windowReturns.reduce((a, b) => a + b, 0) / windowReturns.length;
            const variance = windowReturns.reduce((sum, ret) => sum + Math.pow(ret - mean, 2), 0) / windowReturns.length;
            rollingVol.push(Math.sqrt(variance * 252)); // Annualized
        }

        return rollingVol;
    }

    // Calculate key metrics for an asset
    calculateMetrics(assetData) {
        const returns = assetData.returns;
        const latestReturn = returns[returns.length - 1];
        const avgReturn = returns.reduce((a, b) => a + b, 0) / returns.length;
        const variance = returns.reduce((sum, ret) => sum + Math.pow(ret - avgReturn, 2), 0) / returns.length;
        const volatility = Math.sqrt(variance);
        const totalReturn = assetData.cumulativeReturns[assetData.cumulativeReturns.length - 1];
        const annualizedReturn = avgReturn * 252;
        const annualizedVolatility = volatility * Math.sqrt(252);
        const sharpeRatio = annualizedReturn / annualizedVolatility;
        const maxReturn = Math.max(...returns);
        const minReturn = Math.min(...returns);

        return {
            latestReturn,
            totalReturn,
            annualizedReturn,
            annualizedVolatility,
            sharpeRatio,
            maxReturn,
            minReturn
        };
    }

    // Filter data by date range
    filterDataByPeriod(data, period) {
        const endDate = new Date();
        let startDate;

        switch (period) {
            case '2024':
                startDate = new Date('2024-01-01');
                break;
            case '2023':
                startDate = new Date('2023-01-01');
                endDate.setTime(new Date('2023-12-31').getTime());
                break;
            case 'ytd':
                startDate = new Date(endDate.getFullYear(), 0, 1);
                break;
            default:
                return data; // Return all data
        }

        const filteredData = {};
        
        Object.keys(data).forEach(asset => {
            filteredData[asset] = {
                dates: [],
                prices: [],
                returns: [],
                cumulativeReturns: []
            };

            data[asset].dates.forEach((date, index) => {
                const dateObj = new Date(date);
                if (dateObj >= startDate && dateObj <= endDate) {
                    filteredData[asset].dates.push(date);
                    filteredData[asset].prices.push(data[asset].prices[index]);
                    filteredData[asset].returns.push(data[asset].returns[index]);
                    filteredData[asset].cumulativeReturns.push(data[asset].cumulativeReturns[index]);
                }
            });
        });

        return filteredData;
    }

    // Initialize data loading
    async initialize() {
        this.data = await this.loadRealData();
        return this.data;
    }
}

// Export for use in main dashboard
window.FinancialDataManager = FinancialDataManager;